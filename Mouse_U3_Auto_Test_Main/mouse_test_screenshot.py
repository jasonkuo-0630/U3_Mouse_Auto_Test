# ============================================
# 📌 螢幕截圖模組 - mouse_test_screenshot.py（彈性版）
# 功能：支援多趟測試分別儲存，向下相容未來轉盤系統
# ============================================

import os
import datetime
import pyautogui

def capture_and_save(filename_prefix="Mouse_Test", round_index=1, point=None, log_func=print, angle=None):
    """
    彈性截圖系統：
    - round_index: 測試趟數 (1, 2, 3...) 或未來的角度 (0, 45, 90, 135, 180)
    - point: 測試點名稱 (1m, 2m, 3m...)
    - angle: 可選參數，未來轉盤系統使用
    
    資料夾命名邏輯：
    - 現在：20250619_Mouse_Test_Result_1, Result_2, Result_3...
    - 未來：20250619_Mouse_Test_Angle_0, Angle_45, Angle_90...
    """
    try:
        # 產生時間戳記
        now = datetime.datetime.now()
        today = now.strftime("%Y%m%d")
        timestamp = now.strftime("%H%M%S")
        
        # 設定基礎路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
        base_result_dir = os.path.join(parent_dir, "Result_Screen_Shot")
        
        # 🔧 彈性資料夾命名系統
        if angle is not None:
            # 未來轉盤系統：以角度命名
            folder_suffix = f"Angle_{angle}"
            log_func(f"[Screenshot] 轉盤模式 - 角度: {angle}度")
        else:
            # 現在多趟系統：以趟數命名
            folder_suffix = f"Result_{round_index}"
            log_func(f"[Screenshot] 多趟模式 - 第 {round_index} 趟")
        
        # 建立資料夾
        folder_name = f"{today}_{filename_prefix}_{folder_suffix}"
        result_folder_path = os.path.join(base_result_dir, folder_name)
        
        log_func(f"[Screenshot] 目標資料夾: {result_folder_path}")
        os.makedirs(result_folder_path, exist_ok=True)
        
        # 🔧 檔案命名系統
        if angle is not None:
            # 轉盤系統檔名：20250619_Mouse_Test_1m_90deg_143052.png
            filename = f"{today}_{filename_prefix}_{point}_{angle}deg_{timestamp}.png"
        else:
            # 多趟系統檔名：20250619_Mouse_Test_1m_R1_143052.png
            filename = f"{today}_{filename_prefix}_{point}_R{round_index}_{timestamp}.png"
        
        filepath = os.path.join(result_folder_path, filename)
        log_func(f"[Screenshot] 檔案名稱: {filename}")
        
        # 執行截圖
        log_func("[Screenshot] 開始截圖...")
        pyautogui.screenshot(filepath)
        log_func("[Screenshot] 截圖完成")
        
        # 驗證檔案
        try:
            file_size = os.path.getsize(filepath)
            log_func(f"[Python Screenshot] 🖼️ Saved to: {filepath}")
            log_func(f"[Screenshot] 檔案大小: {file_size:,} bytes")
        except:
            log_func(f"[Python Screenshot] 🖼️ Saved to: {filepath}")
        
        return filepath  # 回傳檔案路徑供後續使用
        
    except Exception as e:
        import traceback
        log_func(f"[Screenshot] ❌ 截圖失敗: {e}")
        log_func(f"[Screenshot] 錯誤詳情: {traceback.format_exc()}")
        return None

# 🔧 未來轉盤系統的輔助函式
def capture_with_angle(filename_prefix="Mouse_Test", angle=0, point=None, log_func=print):
    """
    未來轉盤系統專用的截圖函式
    angle: 轉盤角度 (0, 45, 90, 135, 180)
    """
    return capture_and_save(
        filename_prefix=filename_prefix,
        round_index=None,  # 不使用趟數
        point=point,
        log_func=log_func,
        angle=angle
    )

# 🔧 向下相容：保持原有介面
def capture_and_save_legacy(filename_prefix="Mouse_Test", round_index=1, point=None, log_func=print):
    """
    向下相容的舊版介面，確保現有程式不需修改
    """
    return capture_and_save(
        filename_prefix=filename_prefix,
        round_index=round_index,
        point=point,
        log_func=log_func,
        angle=None
    )