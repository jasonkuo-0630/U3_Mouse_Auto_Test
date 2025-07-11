# =====================v4_輪盤版=====================
# 🔹 主測試流程 - U3_Mouse_Auto_Test_Main_v4.py
# 功能：結合送餐車 WebSocket、HC-12 串口、輪盤角度控制、Sikuli自動化與截圖、LOG功能
# 使用輪盤角度取代原本的趟數迴圈
# =============================================

import asyncio
import os
import time
import datetime
import subprocess
import pyautogui
import pygetwindow as gw
from config import COM_PORT, TURNTABLE_COM_PORT, WS_IP, WS_PORT, TEST_POINT_PATTERN, TEST_POINT_RANGE
from robot_ws_client import RobotWebSocketClient
from serial_util import HC12Serial
from mouse_test_screenshot import capture_with_angle
from log_util import init_log
from turntable_controller import TurntableController

pyautogui.FAILSAFE = False  # 關閉滑鼠移到角落的安全機制

# === 初始參數設定 ===
base_path = os.path.dirname(os.path.abspath(__file__))
sikuli_open = os.path.join(base_path, "U3_Mouse_Test.sikuli")
sikuli_jar = os.path.join(base_path, "sikulixide-2.0.5.jar")
test_type = "Mouse_Test_Turntable"

# === 初始化系統 ===
log_file, log_print = init_log(test_type, base_path)                    # LOG初始化
hc12 = HC12Serial(port=COM_PORT, log_func=log_print)                    # HC-12初始化
turntable = TurntableController(TURNTABLE_COM_PORT, log_func=log_print) # 輪盤初始化

class U3AutoTest:
    """
    U3 輪盤自動化測試主控制類別
    """
    def __init__(self):
        self.client = RobotWebSocketClient(log_func=log_print)
        self.arrival_event = asyncio.Event()
        self.current_target = None

    async def handle_robot_status(self, data):
        """處理小智傳回的狀態訊息"""
        status = data.get("status")
        target = data.get("target")
        log_print(f"[WS] 狀態: {status}, 目標: {target}")

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

    async def run_test_cycle(self):
        """
        執行一次完整的測試週期（輪盤角度版本）
        """
        # 啟動滑鼠測試 GUI
        log_print("[Main] 啟動測試軟體 (Sikuli)...")
        try:
            subprocess.run(["java", "-jar", sikuli_jar, "-r", sikuli_open], timeout=90, stdout=log_file, stderr=log_file, text=True)
        except subprocess.TimeoutExpired:
            log_print("[Sikuli] ❌ 測試軟體開啟超時")
        
        await asyncio.sleep(2)

        # 建立站點列表
        test_points = [TEST_POINT_PATTERN.format(m) for m in TEST_POINT_RANGE]

        # 連接輪盤
        if not turntable.connect():
            log_print("[Error] ❌ 輪盤連接失敗")
            return

        try:
            # 相對角度移動列表（避免線材纏繞）
            test_angles = [0, 45, 45, -135, -45, 90]  # 實際位置: 0° → 45° → 90° → -45° → -90° → 0°
            angle_names = ["正前方", "左45°", "左90°", "右45°", "右90°", "返回原點"]
            actual_positions = [0, 45, 90, -45, -90]  # 用於截圖命名的實際角度
            
            for round_idx, angle in enumerate(test_angles):
                if round_idx == len(test_angles) - 1:
                    # 最後一個：返回原點
                    log_print(f"\n🏁 測試完成，輪盤返回 0°")
                    await turntable.rotate_to_angle(angle)
                    break
                
                round_name = f"第{round_idx + 1}趟"
                angle_name = angle_names[round_idx]
                log_print(f"\n🔄 === {round_name}: {angle_name} ===")
                
                if round_idx == 0:
                    # 第一趟：直接開始測試
                    log_print(f"[Main] 🎯 {round_name}，直接開始測試")
                    await turntable.rotate_to_angle(angle)
                else:
                    # 其他趟：先回到1M再旋轉
                    log_print(f"[Main] 🚀 準備 {round_name}，先回到 1m...")
                    await self.client.send_delivery_command("1m")
                    await self.wait_for_arrival("1m")
                    log_print(f"[Main] 📍 回到 1m，準備旋轉")
                    await asyncio.sleep(3)
                    
                    # 旋轉到目標角度
                    success = await turntable.rotate_to_angle(angle)
                    if not success:
                        log_print(f"[Turntable] ❌ {round_name} 旋轉失敗，跳過")
                        continue
                    await asyncio.sleep(3)

                # 對每個測試點執行測試（保持原本邏輯）
                for test_point in test_points:
                    log_print(f"[Main] 🚀 指派送餐機前往 {test_point}...")
                    await self.client.send_delivery_command(test_point)
                    await self.wait_for_arrival(test_point)
                    log_print(f"[Main] 🎯 抵達 {test_point}，開始測試流程")
                    await asyncio.sleep(3)
                    
                    # HC-12 通訊流程
                    max_retries = 2
                    test_success = False
                    comm_start_time = time.time()
                    
                    for attempt in range(max_retries):
                        log_print(f"[HC-12] 嘗試 {attempt + 1}/{max_retries}: 發送 Robot_Arrived")
                        hc12.send("Robot_Arrived")
                        test_start_received = await hc12.wait_for("Test_Start", timeout=15)
                        
                        if test_start_received:
                            log_print("[HC-12] ✅ 收到 Test_Start，開始測試")
                            test_success = True
                            break
                        else:
                            log_print(f"[HC-12] ❌ 第 {attempt + 1} 次嘗試失敗")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(1)
                    
                    comm_elapsed = time.time() - comm_start_time
                    log_print(f"[DEBUG] HC-12 通訊總耗時: {comm_elapsed:.2f} 秒")
                    
                    if not test_success:
                        log_print(f"[HC-12] ❌ {test_point} 通訊失敗，跳過此測試點")
                        continue
                    
                    # 開始測試
                    test_start_time = time.time()
                    total_wait_sec = 150
                    test_duration = 80
                    
                    pyautogui.press("space")
                    log_print("[Main] ✅ 已按下空白鍵啟動測試錄製")
                    
                    log_print(f"[Main] ⏱️ 等待測試完成 ({test_duration} 秒)...")
                    await asyncio.sleep(test_duration)
                    
                    # 截圖並存檔（使用實際角度命名）
                    log_print("[Main] 📷 測試時間結束，開始截圖...")
                    try:
                        actual_angle = actual_positions[round_idx]
                        capture_with_angle(test_type, actual_angle, test_point, log_func=log_print)
                        log_print("[Main] 📸 已完成截圖並儲存結果")
                    except Exception as e:
                        log_print(f"[Main] ❌ 截圖失敗: {e}")
                    
                    # 補足剩餘停留時間
                    elapsed_since_test_start = time.time() - test_start_time
                    remaining_time = max(total_wait_sec - elapsed_since_test_start, 0)
                    if remaining_time > 0:
                        log_print(f"[Main] ⏱️ 等待剩餘停留時間: {remaining_time:.1f} 秒")
                        await asyncio.sleep(remaining_time)
                    
                    log_print(f"[Main] ✅ {test_point} 測試完成，總耗時: {time.time() - test_start_time:.1f} 秒")
            
        finally:
            turntable.close()

        # 返回原點
        await self.client.send_return()
        log_print("[Main] ✅ 所有測試完成，小智返回原點")
        await asyncio.sleep(3)

        # 結束 LOG
        log_file.write("\n" + "="*50 + "\n")
        log_file.write(f"[LOG END] {datetime.datetime.now()}\n")
        log_file.write("="*50 + "\n\n")

        # 恢復 CMD 視窗
        await asyncio.sleep(0.5)
        for win in gw.getWindowsWithTitle("cmd"):
            if not win.isActive:
                win.activate()
                win.restore()
                win.maximize()

async def main():
    """主程式入口"""
    log_print(f"🎯 U3 無線滑鼠輪盤自動化測試系統")
    log_print("=" * 60)
    log_print(f"🔄 測試角度: 0°, 45°, 90°, -45°, -90° (共 5 趟)")
    
    robot = U3AutoTest()
    
    try:
        # 連接到小智
        await robot.connect(WS_IP, WS_PORT)
        log_print("🔗 已連接到小智")
        
        # 執行輪盤測試循環
        await robot.run_test_cycle()
        
    except Exception as e:
        log_print(f"❌ 發生錯誤: {e}")
        import traceback
        log_print(f"❌ 錯誤詳情: {traceback.format_exc()}")
    finally:
        # 資源清理
        hc12.close()
        log_print("[Main] 🔌 關閉HC-12串口")

        await robot.disconnect()
        log_print("👋 已斷開連接")

        # 強制將 LOG 緩衝寫入檔案並關閉
        log_file.flush()
        log_file.close()

if __name__ == "__main__":
    asyncio.run(main())