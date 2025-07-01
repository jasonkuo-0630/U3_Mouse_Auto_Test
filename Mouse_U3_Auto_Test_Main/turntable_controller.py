# =============================================
# 🔄 輪盤控制模組 - turntable_controller.py
# 功能：簡單的輪盤角度控制，直接發送相對角度指令
# =============================================

import serial
import time
import asyncio

class TurntableController:
    def __init__(self, port, log_func=print):
        self.port = port
        self.log = log_func
        self.ser = None
        
    def connect(self):
        """連接輪盤"""
        try:
            self.ser = serial.Serial(self.port, baudrate=9600, timeout=1)
            time.sleep(2)
            self.log(f"[Turntable] ✅ 輪盤已連接 ({self.port})")
            return True
        except Exception as e:
            self.log(f"[Turntable] ❌ 輪盤連接失敗: {e}")
            return False
    
    async def rotate_to_angle(self, angle):
        """旋轉指定角度（相對移動）"""
        if not self.ser or not self.ser.is_open:
            self.log(f"[Turntable] ❌ 輪盤未連接")
            return False
            
        try:
            command = f"ROTATE_DEGREE:{angle}\n"
            self.ser.write(command.encode())
            self.log(f"[Turntable] 🔄 旋轉 {angle:+}°")
            
            # 等待旋轉完成
            start_time = time.time()
            while time.time() - start_time < 45:
                if self.ser.in_waiting > 0:
                    response = self.ser.readline().decode().strip()
                    if response and "旋轉完成" in response:
                        self.log(f"[Turntable] ✅ 旋轉完成")
                        return True
                await asyncio.sleep(0.1)
            
            self.log(f"[Turntable] ⏰ 旋轉超時")
            return False
            
        except Exception as e:
            self.log(f"[Turntable] ❌ 旋轉失敗: {e}")
            return False
    
    def close(self):
        """關閉連接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.log("[Turntable] 🔌 輪盤連接已關閉")