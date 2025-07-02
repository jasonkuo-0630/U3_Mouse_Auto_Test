# =====================v3========================
# 🔹 主測試流程 - U3_Mouse_Auto_Test_Main.py
# 功能：結合送餐車 WebSocket、HC-12 串口、Sikuli自動化與截圖、LOG功能
# 用於滑鼠產品 U3 測試流程的完整控制腳本
# =============================================

import asyncio
import os
import time
import datetime
import subprocess
import pyautogui
import pygetwindow as gw
from config import COM_PORT, WS_IP, WS_PORT, TEST_POINT_PATTERN, TEST_POINT_RANGE, TEST_ROUNDS
from robot_ws_client import RobotWebSocketClient  # 小智 WebSocket 客戶端
from serial_util import HC12Serial                # HC-12 串口控制模組
from mouse_test_screenshot import capture_and_save  # 螢幕截圖模組
from log_util import init_log                     # LOG 紀錄初始化工具

pyautogui.FAILSAFE = False  # 關閉滑鼠移到角落的安全機制

# === 初始參數設定 ===
base_path = os.path.dirname(os.path.abspath(__file__))  # 目前.py所在資料夾
sikuli_open = os.path.join(base_path, "U3_Mouse_Test.sikuli")  # Sikuli 測試腳本
sikuli_jar = os.path.join(base_path, "sikulixide-2.0.5.jar")    # Sikuli 執行器
test_type = "Mouse_Test"       # 測試類型標記字串(基本上不必修改 不過未來也可修改為"專案名稱_MS")

# === 初始化 LOG 系統
log_file, log_print = init_log(test_type, base_path)

# === 初始化 HC-12 ===
hc12 = HC12Serial(port=COM_PORT, log_func=log_print) # ✅ Arduino HC-12 實際使用的 COM port(自行去config.py更改)

# === 類別函式庫定義(配合小智的呼叫函式) ===
class U3AutoTest:
    """
    U3 自動化測試主控制類別。
    結合送餐車、HC-12、Sikuli、截圖與 LOG 等Python模組。
    """
    def __init__(self):
        self.client = RobotWebSocketClient(log_func=log_print)
        self.arrival_event = asyncio.Event()
        self.current_target = None

    # === 狀態監聽回呼函式 ===
    async def handle_robot_status(self, data):
        """
        處理小智傳回的狀態訊息，當抵達指定站點時觸發 arrived_event。
        """
        status = data.get("status")
        target = data.get("target")
        log_print(f"[WS] 狀態: {status}, 目標: {target}")

        # 檢查是否到達目標位置
        if status == "arrived" and target == self.current_target:
            log_print(f"[WS] ✅ 到達 {target}")
            self.arrival_event.set()

    async def wait_for_arrival(self, target):
        """等待到達指定目標"""
        self.current_target = target
        self.arrival_event.clear()
        await self.arrival_event.wait()

    async def connect(self, ip, port):
        """連接到小智"""
        self.client.set_message_handler(self.handle_robot_status)
        await self.client.connect(ip, port)
        
    async def disconnect(self):
        """斷開連接"""
        await self.client.disconnect()

    # === 主測試流程 ===
    async def run_test_cycle(self):
        """
        執行一次完整的測試週期：
        1. 啟動測試軟體（透過Sikuli開啟，並等待測試）
        2. 指派小智前往指定測試點
        3. 與 Arduino 通訊控制滾輪
        4. 開始測試 → 截圖 → 等待時間補足
        5. 測試完成後送餐車返回，並結束 LOG
        """
        # 啟動滑鼠測試 GUI（由 Sikuli 自動化開啟）
        log_print("[Main] 啟動測試軟體 (Sikuli)...")
        try:
            subprocess.run(["java", "-jar", sikuli_jar, "-r", sikuli_open], timeout=90, stdout=log_file, stderr=log_file, text=True)
        except subprocess.TimeoutExpired:
            log_print("[Sikuli] ❌ 測試軟體開啟超時")
        
        await asyncio.sleep(2)  # 預留啟動時間

        # 建立站點列表（根據命名規則自動生成）
        test_points = [TEST_POINT_PATTERN.format(m) for m in TEST_POINT_RANGE]

        for round_num in range(TEST_ROUNDS):
            log_print(f"🔁 第 {round_num + 1} 趟測試開始")

            for test_point in test_points:
                log_print(f"[Main] 🚀 指派送餐機前往 {test_point}...")
                await self.client.send_delivery_command(test_point)
                await self.wait_for_arrival(test_point)
                log_print(f"[Main] 🎯 抵達 {test_point}，開始測試流程")
                await asyncio.sleep(3)  # 等待車身回穩
                
                # === 改進的 HC-12 通訊流程（進一步優化時間）===
                max_retries = 2  # 重試 2 次
                test_success = False
                comm_start_time = time.time()
                
                for attempt in range(max_retries):
                    log_print(f"[HC-12] 嘗試 {attempt + 1}/{max_retries}: 發送 Robot_Arrived")
                    
                    # 發送指令給 Arduino
                    hc12.send("Robot_Arrived")
                    
                    # 進一步縮短 timeout 到 15 秒（你的 Debug.py 都很快成功）
                    test_start_received = await hc12.wait_for("Test_Start", timeout=15)
                    
                    if test_start_received:
                        log_print("[HC-12] ✅ 收到 Test_Start，開始測試")
                        test_success = True
                        break
                    else:
                        log_print(f"[HC-12] ❌ 第 {attempt + 1} 次嘗試失敗")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)  # 縮短重試間隔到 1 秒
                
                # 記錄通訊耗時
                comm_elapsed = time.time() - comm_start_time
                log_print(f"[DEBUG] HC-12 通訊總耗時: {comm_elapsed:.2f} 秒")
                
                if not test_success:
                    log_print(f"[HC-12] ❌ {test_point} 通訊失敗，跳過此測試點")
                    continue  # 跳過這個測試點，繼續下一個
                
                # === 只有在通訊成功後才開始測試（重新計時）===
                test_start_time = time.time()  # 重新設定測試開始時間
                total_wait_sec = 150  # 調整為 2.5 分鐘，給截圖留時間
                test_duration = 80
                
                # 啟動測試錄製
                pyautogui.press("space")
                log_print("[Main] ✅ 已按下空白鍵啟動測試錄製")
                
                # 固定等待測試時間（80 秒）
                log_print(f"[Main] ⏱️ 等待測試完成 ({test_duration} 秒)...")
                await asyncio.sleep(test_duration)
                
                # 截圖並存檔
                log_print("[Main] 📷 測試時間結束，開始截圖...")
                try:
                    capture_and_save(test_type, round_num+1, test_point, log_func=log_print)
                    log_print("[Main] 📸 已完成截圖並儲存結果")
                except Exception as e:
                    log_print(f"[Main] ❌ 截圖失敗: {e}")
                
                # 補足剩餘停留時間（確保總共停留 150 秒）
                elapsed_since_test_start = time.time() - test_start_time
                remaining_time = max(total_wait_sec - elapsed_since_test_start, 0)
                if remaining_time > 0:
                    log_print(f"[Main] ⏱️ 等待剩餘停留時間: {remaining_time:.1f} 秒")
                    await asyncio.sleep(remaining_time)
                
                log_print(f"[Main] ✅ {test_point} 測試完成，總耗時: {time.time() - test_start_time:.1f} 秒")
            
        # 返回原點
        await self.client.send_return()
        log_print(f"[Main] ✅ 所有 {TEST_ROUNDS} 趟測試完成，小智返回原點")
        await asyncio.sleep(3) 

        # 結束 LOG
        log_file.write("\n" + "="*50 + "\n")
        log_file.write(f"[LOG END] {datetime.datetime.now()}\n")
        log_file.write("="*50 + "\n\n")

        # === 恢復並最大化 CMD 視窗 ===
        await asyncio.sleep(0.5)
        for win in gw.getWindowsWithTitle("cmd"):
            if not win.isActive:
                win.activate()
                win.restore()
                win.maximize()
    
async def main():
    robot = U3AutoTest()
    
    try:
        # 連接到機器人
        await robot.connect(WS_IP, WS_PORT)  # 修改為實際IP(自行去config.py修改)
        log_print("🔗 已連接到小智")
        
        # 執行測試循環
        await robot.run_test_cycle()
        
    except Exception as e:
        log_print(f"❌ 發生錯誤: {e}")
    finally:
         # === 測試結束後： 資源清理 ===
        hc12.close()
        log_print("[Main] 關閉HC-12串口")

        await robot.disconnect()
        log_print("👋 已斷開連接")

        # === 強制將 LOG 緩衝寫入檔案並關閉 ===
        log_file.flush()
        log_file.close()

if __name__ == "__main__":
    asyncio.run(main())