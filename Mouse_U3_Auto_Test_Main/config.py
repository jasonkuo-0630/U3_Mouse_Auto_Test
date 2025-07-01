# =============================================
# 🔹 設定檔 - config.py
# 功能：設定相關基礎設定
# =============================================

COM_PORT = "COM3"
TURNTABLE_COM_PORT = "COM5"    # 輪盤控制 COM Port
WS_IP = "192.168.0.225"
WS_PORT = 8000                 # 小智 WebSocket Port

# 測試點命名方式：支援格式化字串，例如 'A{:02d}'、'{:d}M' 等
TEST_POINT_PATTERN = '{:d}m'   # 預設為 1m ~ 5m（可改為 'A{:02d}' 則是 A01 ~ A05）
TEST_POINT_RANGE = range(1, 6) # 站點編號範圍

TEST_ROUNDS = 3  # 測試趟數（想要跑幾次 1~10 全部來回就改這邊）