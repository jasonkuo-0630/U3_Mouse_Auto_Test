# =====================v2========================
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

        for round in range(TEST_ROUNDS):  # 跑指定次數
            log_print(f"🔁 第 {round + 1} 趟測試開始")

            for test_point in test_points:
                log_print(f"[Main] 🚀 指派送餐機前往 {test_point}...")
                await self.client.send_delivery_command(test_point)
                await self.wait_for_arrival(test_point)
                log_print(f"[Main] 🎯 抵達 {test_point}，開始測試流程")
                
                # 測試時間參數
                total_wait_sec = 150  # 總等待時間 2.5 分鐘
                test_duration = 80    # 實際錄製時間 80 秒
                relay_duration = 70   # 繼電器滑鼠滾輪啟動時間（無意義變數 交由 Arduino 控制 主程式不使用此變數）

                start_time = time.time()

                # === 通知 Arduino 開啟滾輪（開始測試前置）===
                hc12.send("Robot_Arrived")
                log_print("[HC-12] 傳送 Robot_Arrived 給 Arduino，啟動繼電器")

                # 等待 Arduino 回傳 "Test_Start" 指令
                await hc12.wait_for("Test_Start")
                log_print("[HC-12] 收到 Test_Start，開始按下空白鍵")

                # 啟動測試錄製流程（模擬按下空白鍵）
                pyautogui.press("space")
                log_print("[Main] ✅ 已按下空白鍵啟動測試錄製")

                # 等待錄製時間結束前，不進行截圖
                elapsed = time.time() - start_time
                remaining_for_test = max(test_duration - elapsed, 0)
                await asyncio.sleep(remaining_for_test)

                # 截圖並存檔（自動建立資料夾與圖片編號）
                capture_and_save(test_type, round+1, test_point, log_func=log_print) # 擷取當前螢幕畫面，並依照測試類型建立資料夾分類儲存
                log_print("[Main] 📸 已完成截圖並儲存結果")

                # 補足完整 150 秒倒數（確保測試秒數一致性）
                elapsed = time.time() - start_time
                remaining_time = max(total_wait_sec - elapsed, 0)
                if remaining_time > 0:
                    await asyncio.sleep(remaining_time)

                
            await self.client.send_return()
            log_print("[Main] 測試完成，小智返回原點")
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
        
        # 執行 20 次循環
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

#=================================v0.1 Debug-Pass====================================== 
# v0.1 - 確認 WebSocket + 小智移動沒問題，HC12 暫時不介入
# 測試流程：連線 → 前往 1M → 等待 2 分鐘 → 返回原點

import asyncio
import datetime
from config import WS_IP, WS_PORT
from robot_ws_client import RobotWebSocketClient
from log_util import init_log

# === 初始化 LOG ===
log_file, log_print = init_log("Base_Test", ".")

class SimpleTest:
    def __init__(self):
        self.client = RobotWebSocketClient(log_func=log_print)
        self.arrival_event = asyncio.Event()
        self.current_target = None

    async def handle_status(self, data):
        status = data.get("status")
        target = data.get("target")
        log_print(f"[WS] 狀態: {status}, 目標: {target}")
        if status == "arrived" and target == self.current_target:
            log_print(f"[WS] ✅ 抵達 {target}")
            self.arrival_event.set()

    async def wait_for_arrival(self, target):
        self.current_target = target
        self.arrival_event.clear()
        await self.arrival_event.wait()

    async def run(self):
        try:
            self.client.set_message_handler(self.handle_status)
            await self.client.connect(WS_IP, WS_PORT)
            log_print("🔗 已連接到小智")
            await asyncio.sleep(2) # 等待兩秒緩衝

            # === 前往 1M ===
            test_point = "1m"
            log_print(f"[Main] 🚀 指派送餐車前往 {test_point}")
            await self.client.send_delivery_command(test_point)
            await self.wait_for_arrival(test_point)
            log_print(f"[Main] 🎯 抵達 {test_point}，等待 2 分鐘")

            await asyncio.sleep(120)  # 等待兩分鐘

            # === 返回原點 ===
            await self.client.send_return()
            log_print("[Main] 🏁 測試結束，小智返回原點")
            await asyncio.sleep(3)

        except Exception as e:
            log_print(f"❌ 發生錯誤: {e}")
        finally:
            await self.client.disconnect()
            log_print("👋 已斷開連接")
            log_file.write(f"\n[LOG END] {datetime.datetime.now()}\n")
            log_file.flush()
            log_file.close()

async def main():
    await SimpleTest().run()

if __name__ == "__main__":
    asyncio.run(main())

#=================================v0.2 Debug-Pass====================================== 
# v0.2 - 確認 WebSocket + 小智移動沒問題，HC12 暫時不介入
# 測試流程：連線 → 前往 1M ~ 5M → 等待 2 分鐘 → 返回原點

import asyncio
import time
from config import WS_IP, WS_PORT, TEST_POINT_PATTERN
from robot_ws_client import RobotWebSocketClient
from log_util import init_log

log_file, log_print = init_log("Base_Test", ".")

class SimpleTest:
    def __init__(self):
        self.client = RobotWebSocketClient(log_func=log_print)
        self.arrival_event = asyncio.Event()
        self.current_target = None

    async def handle_status(self, data):
        status = data.get("status")
        target = data.get("target")
        log_print(f"[WS] 狀態: {status}, 目標: {target}")
        if status == "arrived" and target == self.current_target:
            log_print(f"[WS] ✅ 到達 {target}")
            self.arrival_event.set()

    async def wait_for_arrival(self, target):
        self.current_target = target
        self.arrival_event.clear()
        await self.arrival_event.wait()

    async def run(self):
        await self.client.connect(WS_IP, WS_PORT)
        self.client.set_message_handler(self.handle_status)
        log_print("🔗 已連接到小智")
        
        await asyncio.sleep(2) # 緩衝兩秒

        # 測試 1~5M
        for i in range(1, 6):
            point = TEST_POINT_PATTERN.format(i)
            log_print(f"[Main] 🚀 前往 {point} 中...")
            await self.client.send_delivery_command(point)
            await self.wait_for_arrival(point)
            log_print(f"[Main] ⏳ 到達 {point}，等待 2 分鐘...")
            await asyncio.sleep(120) # 等待測試時間

        await self.client.send_return()
        log_print("[Main] 🚗 小智已發送返回原點")
        await asyncio.sleep(2) #緩衝兩秒

        await self.client.disconnect()
        log_print("👋 已斷開連接")
        log_file.flush()
        log_file.close()

async def main():
    test = SimpleTest()
    await test.run()

if __name__ == "__main__":
    asyncio.run(main())

