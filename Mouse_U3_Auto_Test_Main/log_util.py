# ============================================
# 📌 LOG 控制模組 - log_util.py（自動避開重複命名）
# 功能：建立 LOG 檔並避免覆蓋，輸出 CMD 與檔案同步紀錄
# ============================================

import os
import datetime

def init_log(test_type="Mouse_Test", base_path="."):
    """
    初始化 LOG 紀錄系統，根據今日日期與測試類型自動產生不重複的 LOG 檔案。
    傳回兩個物件：
    - log_file：檔案寫入控制物件
    - log_print(msg)：自訂的印出函式，會同時印出到畫面與 log 檔
    """

    # 取得今天日期（格式：2025-05-21），作為 LOG 檔名的一部分
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 設定 LOG 存放目錄（預設為主程式上層的 LOG 資料夾）
    log_dir = os.path.abspath(os.path.join(base_path, "../LOG"))
    os.makedirs(log_dir, exist_ok=True)  # 如果資料夾不存在則自動建立

    # 建立遞增命名邏輯（避免重複覆蓋）
    index = 1
    while True:
        log_filename = f"{today}_{test_type}_LOG_{index}.txt"  # ex: 2025-05-21_Mouse_Test_LOG_1.txt
        log_path = os.path.join(log_dir, log_filename)
        if not os.path.exists(log_path):
            break  # 找到第一個尚未被使用的檔名
        index += 1  # 若已存在，往下編號直到不衝突為止

    # 開啟 log 檔案進行寫入（UTF-8 格式）
    log_file = open(log_path, "w", encoding="utf-8")

    # 寫入開頭標記與測試類型資訊
    log_file.write(f"[LOG START] {datetime.datetime.now()}\n")
    log_file.write(f"=== 測試類型：{test_type} ===\n\n")

    # 建立 log_print 函式：同時輸出到終端與檔案
    def log_print(msg):
        print(msg)               # 印在 CMD 螢幕
        print(msg, file=log_file)  # 寫入 LOG 檔

    # 回傳 log 檔案物件 與 印出函式
    return log_file, log_print
