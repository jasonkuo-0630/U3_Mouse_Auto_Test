import serial
import time

class HC12Controller:
    def __init__(self, port, baudrate=9600):
        """
        初始化HC-12控制器
        port: COM埠 (Windows: 'COM3', Linux/Mac: '/dev/ttyUSB0')
        """
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"已連接到 {port}")
            time.sleep(2)  # 等待HC-12初始化
        except Exception as e:
            print(f"連接失敗: {e}")
            self.ser = None
    
    def send_message(self, message):
        """發送訊息"""
        if self.ser and self.ser.is_open:
            self.ser.write(message.encode())
            print(f"已發送: {message}")
            return True
        return False
    
    def read_message(self, timeout=5):
        """讀取回復訊息"""
        if not self.ser or not self.ser.is_open:
            return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                message = self.ser.readline().decode().strip()
                print(f"收到回復: {message}")
                return message
            time.sleep(0.1)
        
        print("等待回復超時")
        return None
    
    def close(self):
        """關閉連線"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("連線已關閉")

def main():
    # 設定你的COM埠
    PORT = 'COM3'  # Windows範例，Linux/Mac可能是 '/dev/ttyUSB0'
    
    # 建立HC-12控制器
    hc12 = HC12Controller(PORT)
    
    if hc12.ser is None:
        return
    
    try:
        while True:
            # 發送"Arrived"指令
            command = input("按Enter發送'Arrived'指令 (或輸入'q'退出): ")
            
            if command.lower() == 'q':
                break
            
            # 發送指令
            if hc12.send_message("Robot_Arrived"):
                # 等待Arduino回復
                response = hc12.read_message(timeout=10)
                
                if response == "Test_Start":
                    print("✓ 繼電器已成功啟動！")
                elif response:
                    print(f"收到意外回復: {response}")
                else:
                    print("✗ 未收到回復")
            
            print("-" * 40)
    
    except KeyboardInterrupt:
        print("\n程式中斷")
    
    finally:
        hc12.close()

if __name__ == "__main__":
    main()