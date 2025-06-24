# ============================================
# 🔹 HC-12 互對通訊模組（修復版）- serial_util.py 
# 功能：傳送 Robot_Arrived → 等待 Test_Start → 關閉
# ============================================

import serial
import time
import asyncio

class HC12Serial:
    def __init__(self, port, baudrate=9600, timeout=1, log_func=print):
        self.log = log_func
        """
        初始化 HC-12 串口連線
        """
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            self.log(f"[HC-12] ✅ 已開啟串口: {port}")
            time.sleep(2)  # 給 HC-12 初始化時間
        except serial.SerialException as e:
            self.log(f"[HC-12] ❌ 串口開啟失敗: {e}")
            self.ser = None

    def send(self, msg):
        """
        傳送任意訊息（與 Debug.py 格式一致，不加換行符）
        """
        if self.ser and self.ser.is_open:
            # 清空接收緩衝區，避免舊資料干擾
            self.ser.reset_input_buffer()
            
            # 使用與 Debug.py 相同的格式
            raw_data = msg.encode("utf-8")
            self.ser.write(raw_data)
            self.log(f"[HC-12] ✅ 傳送: {msg}")
        else:
            self.log("[HC-12] ❌ 串口尚未開啟")

    async def wait_for(self, expected, timeout=30):
        """
        等待特定訊息出現（含 timeout 防止卡死）
        改進版：更穩定的資料讀取
        """
        if not self.ser or not self.ser.is_open:
            self.log("[HC-12] ❌ 串口尚未開啟，無法等待訊息")
            return False

        self.log(f"[HC-12] 🔍 等待訊息: '{expected}' (timeout: {timeout}秒)")
        start_time = time.time()
        
        while True:
            current_time = time.time()
            if current_time - start_time > timeout:
                self.log(f"[HC-12] ⏰ 等待 '{expected}' 超時 ({timeout}秒)")
                return False

            if self.ser.in_waiting > 0:
                try:
                    # 使用與 Debug.py 相同的讀取方式
                    msg = self.ser.readline().decode('utf-8').strip()
                    if msg:
                        self.log(f"[HC-12] 📩 收到: '{msg}'")
                        if msg == expected:
                            self.log(f"[HC-12] ✅ 成功匹配訊息: '{expected}'")
                            return True
                        else:
                            self.log(f"[HC-12] ℹ️ 訊息不匹配，繼續等待...")
                except UnicodeDecodeError as e:
                    self.log(f"[HC-12] ⚠️ 解碼錯誤: {e}")
                except Exception as e:
                    self.log(f"[HC-12] ⚠️ 讀取錯誤: {e}")
            
            await asyncio.sleep(0.1)  # 減少 CPU 使用率

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.log("[HC-12] 串口已關閉")
        else:
            self.log("[HC-12] ❗️串口未開啟或已關閉")