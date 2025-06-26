# =============================================
# 🔹 輪盤系統獨立測試 - turntable_test.py
# 功能：測試步進馬達旋轉功能，驗證通訊正常
# =============================================

import serial
import time

port="COM5"

class SimpleTurntableTest:
    """
    簡化的輪盤測試類別
    用於驗證基本功能
    """
    
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
    def connect(self):
        """連接到輪盤 Arduino"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # 等待 Arduino 重置
            print(f"✅ 已連接到輪盤系統 ({self.port})")
            
            # 讀取 Arduino 初始化訊息
            initial_msg = self.ser.readline().decode().strip()
            if initial_msg:
                print(f"Arduino: {initial_msg}")
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def rotate_test(self, angle):
        """測試旋轉到指定角度"""
        if not self.ser or not self.ser.is_open:
            print("❌ 未連接")
            return False
            
        try:
            # 發送旋轉指令
            command = f"ROTATE_DEGREE:{angle}\n"
            self.ser.write(command.encode())
            print(f"📤 發送指令: ROTATE_DEGREE:{angle}")
            
            # 等待回應
            start_time = time.time()
            while time.time() - start_time < 30:  # 30秒超時
                if self.ser.in_waiting > 0:
                    response = self.ser.readline().decode().strip()
                    if response:
                        print(f"📥 Arduino: {response}")
                        if "旋轉完成" in response:
                            print(f"✅ 旋轉到 {angle}° 完成")
                            return True
                time.sleep(0.1)
            
            print("⏰ 等待回應超時")
            return False
            
        except Exception as e:
            print(f"❌ 旋轉失敗: {e}")
            return False
    
    def close(self):
        """關閉連接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("🔌 連接已關閉")

def main():
    """
    輪盤測試主程式
    """
    print("🔧 輪盤系統獨立測試")
    print("=" * 40)
    
    # 可以修改這裡的 COM Port
    turntable = SimpleTurntableTest(port)  # 改成你的實際 COM Port
    
    if not turntable.connect():
        print("無法連接，程式結束")
        return
    
    try:
        # 測試角度列表
        test_angles = [0, 45, 90, 135, 180, 0]  # 最後回到 0 度
        
        for angle in test_angles:
            print(f"\n🔄 測試旋轉到 {angle}°...")
            success = turntable.rotate_test(angle)
            
            if success:
                print(f"✅ {angle}° 測試成功")
                # 穩定等待時間
                print("⏳ 等待 3 秒穩定時間...")
                time.sleep(3)
            else:
                print(f"❌ {angle}° 測試失敗")
                break
        
        print("\n🎉 輪盤測試完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷測試")
    
    finally:
        turntable.close()

def interactive_test():
    """
    互動式測試模式（支援正負角度）
    """
    print("🔧 輪盤互動測試模式（支援 ±360 度）")
    print("=" * 40)
    
    turntable = SimpleTurntableTest(port)  # 改成你的實際 COM Port
    
    if not turntable.connect():
        print("無法連接，程式結束")
        return
    
    try:
        while True:
            angle_input = input("\n輸入角度 (-360 到 360)，或 'q' 退出: ")
            
            if angle_input.lower() == 'q':
                break
            
            try:
                angle = int(angle_input)
                if -360 <= angle <= 360:
                    print(f"🔄 旋轉到 {angle}°...")
                    turntable.rotate_test(angle)
                else:
                    print("⚠️ 請輸入 -360 到 360 之間的角度")
            except ValueError:
                print("⚠️ 無效輸入：請輸入整數度數")
    
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷")
    
    finally:
        turntable.close()

if __name__ == "__main__":
    print("選擇測試模式:")
    print("1. 自動測試 (0°→45°→90°→135°→180°→0°)")
    print("2. 互動測試 (手動輸入角度)")
    
    choice = input("請選擇 (1 或 2): ")
    
    if choice == "1":
        main()
    elif choice == "2":
        interactive_test()
    else:
        print("無效選擇")