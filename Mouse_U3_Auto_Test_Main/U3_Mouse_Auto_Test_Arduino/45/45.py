import tkinter as tk
import serial
import serial.tools.list_ports # 雖然我們直接指定埠，但保留它以防萬一

import time

# --- 序列通訊設定 ---
# 直接指定 Arduino 的 COM 埠為 'COM12'
arduino_port = 'COM6' # <--- 你的 Arduino 在 COM12
ser = None # 全局序列物件

def find_arduino_port():
    # 當 arduino_port 已經被明確指定時，這個函式就不再需要自動偵測了
    if arduino_port:
        return True
    return False

def connect_to_arduino():
    global ser
    if arduino_port:
        try:
            ser = serial.Serial(arduino_port, 9600, timeout=1) # 9600 鮑率，1 秒超時
            time.sleep(2) # 給 Arduino 時間在序列連線後重置
            update_status(f"已連接到 Arduino ({arduino_port})！")
            # 連接成功後啟用輸入框和旋轉按鈕
            degree_entry.config(state=tk.NORMAL)
            rotate_button.config(state=tk.NORMAL)
        except serial.SerialException as e:
            update_status(f"連接錯誤: {e}。請檢查 {arduino_port} 是否正確或已被其他程式佔用。")
            degree_entry.config(state=tk.DISABLED)
            rotate_button.config(state=tk.DISABLED)
    else:
        update_status("錯誤：未指定 Arduino 埠號。")
        degree_entry.config(state=tk.DISABLED)
        rotate_button.config(state=tk.DISABLED)

def disconnect_from_arduino():
    global ser
    if ser and ser.is_open:
        ser.close()
        ser = None
        update_status("已從 Arduino 斷開連接。")
        degree_entry.config(state=tk.DISABLED)
        rotate_button.config(state=tk.DISABLED)

# --- GUI 函式 ---
def rotate_motor_by_input():
    if ser and ser.is_open:
        try:
            degrees_str = degree_entry.get() # 獲取輸入框中的文字
            try:
                degrees = int(degrees_str) # 嘗試將文字轉換為整數
                if -360 <= degrees <= 360: # 可以限制旋轉角度範圍，例如 -360 到 360
                    command = f"ROTATE_DEGREE:{degrees}\n" # 組合成新的指令格式
                    ser.write(command.encode()) # 將字串編碼為位元組
                    update_status(f"指令已發送: {command.strip()}。等待 Arduino 回應...")
                    # 可選：讀取 Arduino 的回應
                    response = ser.readline().decode().strip()
                    if response:
                        update_status(f"Arduino 回應: {response}")
                    else:
                        update_status("未收到 Arduino 的即時回應。")
                else:
                    update_status("請輸入 -360 到 360 之間的度數。") # 提示使用者有效範圍
            except ValueError:
                update_status("無效輸入：請輸入一個整數度數。") # 處理非數字輸入
        except serial.SerialException as e:
            update_status(f"序列錯誤: {e}。嘗試重新連接...")
            disconnect_from_arduino()
            connect_to_arduino()
    else:
        update_status("未連接到 Arduino。請先連接。")

def update_status(message):
    status_label.config(text=message)

# --- GUI 設定 ---
root = tk.Tk()
root.title("Arduino 步進馬達控制器")
root.geometry("450x250") # 稍微加大視窗以容納新元素

# 狀態標籤
status_label = tk.Label(root, text="狀態: 未連接", fg="blue")
status_label.pack(pady=10)

# 連接/斷開按鈕
connect_frame = tk.Frame(root)
connect_frame.pack(pady=5)

connect_button = tk.Button(connect_frame, text=f"連接到 Arduino ({arduino_port})", command=connect_to_arduino)
connect_button.pack(side=tk.LEFT, padx=5)

disconnect_button = tk.Button(connect_frame, text="斷開連接", command=disconnect_from_arduino)
disconnect_button.pack(side=tk.RIGHT, padx=5)

# 度數輸入框和標籤
degree_frame = tk.Frame(root)
degree_frame.pack(pady=10)

degree_label = tk.Label(degree_frame, text="輸入度數:")
degree_label.pack(side=tk.LEFT)

degree_entry = tk.Entry(degree_frame, width=10, font=("Arial", 12))
degree_entry.pack(side=tk.LEFT, padx=5)
degree_entry.insert(0, "45") # 預設輸入框為 45 度
degree_entry.config(state=tk.DISABLED) # 初始禁用

# 旋轉確認按鈕
rotate_button = tk.Button(root, text="確認旋轉", command=rotate_motor_by_input, font=("Arial", 16), bg="lightgreen")
rotate_button.pack(pady=10)
rotate_button.config(state=tk.DISABLED) # 初始禁用

# 關閉時，確保序列埠已關閉
def on_closing():
    if ser and ser.is_open:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# 初始連接嘗試
connect_to_arduino()

root.mainloop()