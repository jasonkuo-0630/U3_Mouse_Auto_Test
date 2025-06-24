# U3 滑鼠自動測試系統

## 📖 專案簡介
自動化滑鼠滾輪測試系統，結合送餐機器人移動平台、HC-12 無線通訊、Arduino 繼電器控制、Sikuli 自動化測試與螢幕截圖功能，實現完全無人化的滑鼠產品測試流程。

## 🏗️ 系統架構
- **主控程式**: Python 3.10+ (asyncio 非同步架構)
- **移動平台**: 送餐機器人 (WebSocket 控制)
- **通訊模組**: HC-12 無線模組 (433MHz)
- **控制系統**: Arduino UNO + 繼電器模組
- **測試軟體**: Sikuli IDE 自動化測試
- **驅動設備**: 滑鼠滾輪馬達
- **記錄系統**: 自動截圖 + LOG 記錄

## ⚡ 系統特色
- ✅ **完全無人化測試**：支援夜間自動執行
- ✅ **多趟次測試**：可設定 1~N 趟連續測試
- ✅ **智能路徑規劃**：機器人自動最佳化移動路徑
- ✅ **通訊容錯機制**：HC-12 重試機制確保穩定性
- ✅ **時間精確控制**：Arduino 70秒 + PC 80秒 同步執行
- ✅ **自動結果記錄**：截圖 + LOG 雙重記錄
- ✅ **向下相容設計**：支援未來轉盤系統擴展

## 🔧 硬體配置

### Arduino UNO 接線圖
```
Arduino UNO:
├── Vin ────── 電池盒正極 (18650 三串 11V)
├── GND ────── 電池盒負極、HC-12 GND、繼電器 GND
├── D2  ────── HC-12 TXD (程式設定為 Rx)
├── D3  ────── HC-12 RXD (程式設定為 Tx)
├── D7  ────── 繼電器 IN
├── D13 ────── LED 狀態指示燈
└── 5V  ────── 繼電器 VCC、HC-12 VCC

繼電器模組:
├── VCC ────── Arduino 5V
├── GND ────── Arduino GND
├── IN  ────── Arduino D7
├── NO  ────── 滑鼠滾輪馬達正極
└── COM ────── 電池盒正極

滑鼠滾輪馬達:
├── 正極 ───── 繼電器 NO
└── 負極 ───── 電池盒負極

HC-12 無線模組:
├── VCC ────── Arduino 5V
├── GND ────── Arduino GND
├── TXD ────── Arduino D2 (Rx)
└── RXD ────── Arduino D3 (Tx)
```

### 電源配置
- **Arduino 供電**: 18650 鋰電池三串 (11V)
- **HC-12 供電**: Arduino 5V 輸出
- **繼電器供電**: Arduino 5V 輸出
- **滑鼠馬達**: 電池盒直接供電 (透過繼電器開關)

## 💻 軟體環境

### Python 環境需求
```bash
# Python 版本
Python 3.10+

# 必要套件安裝
pip install pyautogui pygetwindow websockets pyserial asyncio
```

### 必要軟體
- **Java JDK 17+**: 用於執行 Sikuli IDE
- **Arduino IDE**: 用於燒錄 Arduino 程式 (可選)

### 📁 必要檔案結構 (重要！)
```
Mouse_U3_Auto_Test_Main/
├── U3_Mouse_Auto_Test_Main.py
├── config.py
├── serial_util.py
├── mouse_test_screenshot.py
├── robot_ws_client.py
├── log_util.py
├── sikulixide-2.0.5.jar          # ⚠️ 必須放在此資料夾內！
└── U3_Mouse_Test.sikuli/         # ⚠️ Sikuli 測試腳本資料夾
```

**⚠️ 重要提醒**：
- `sikulixide-2.0.5.jar` **必須放在與主程式相同的資料夾內**
- `U3_Mouse_Test.sikuli` 資料夾也必須在相同位置
- 如果檔案位置錯誤，程式會無法啟動 Sikuli 測試軟體

### 驅動程式
- **CP2102 USB 轉串口驅動**: [下載連結](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

## ⚙️ 設定檔說明

### config.py 參數配置
```python
# 硬體設定
COM_PORT = "COM3"              # HC-12 串口號
WS_IP = "192.168.0.225"        # 送餐機器人 IP 位址
WS_PORT = 8000                 # WebSocket 連接埠

# 測試點設定
TEST_POINT_PATTERN = '{:d}m'   # 測試點命名格式 (1m, 2m, 3m...)
TEST_POINT_RANGE = range(1, 6) # 測試點範圍 (1~5m)

# 測試參數
TEST_ROUNDS = 3                # 測試趟數 (執行 3 趟完整測試)
```

## 🚀 使用方式

### 1. 硬體準備
- [x] 確保 Arduino 電池電量充足 (11V+)
- [x] 檢查 HC-12 模組 LED 燈號正常
- [x] 確認滑鼠滾輪馬達正常運作
- [x] 啟動送餐機器人系統

### 2. 軟體準備
- [x] 確認 COM Port 設定正確
- [x] **確認 sikulixide-2.0.5.jar 在正確位置** (與主程式同資料夾)
- [x] **確認 U3_Mouse_Test.sikuli 資料夾存在**
- [x] 測試 HC-12 通訊 (可使用 Debug.py)
- [x] 確認送餐機器人 WebSocket 連線正常

### 3. 執行測試
```bash
# 進入程式目錄
cd U3_Mouse_Auto_Test

# 執行主程式
python U3_Mouse_Auto_Test_Main.py
```

### 4. 測試流程自動執行
```
1. 🚀 自動啟動 Sikuli 測試軟體
2. 🎯 機器人依序移動到測試點 (1m → 2m → 3m → 4m → 5m)
3. 📡 HC-12 通訊控制 Arduino 啟動滾輪 (70 秒)
4. ⌨️  自動按下空白鍵開始測試錄製 (80 秒)
5. 📸 自動截圖保存測試結果
6. 🔄 重複執行設定的趟數
7. 🏠 所有測試完成後機器人返回原點
```

## 📊 輸出結果

### LOG 檔案格式
```
路徑: ../LOG/
格式: YYYY-MM-DD_Mouse_Test_LOG_N.txt
範例: 2025-06-19_Mouse_Test_LOG_1.txt

內容包含:
- 詳細執行步驟記錄
- HC-12 通訊狀態
- 時間控制資訊
- 錯誤處理記錄
```

### 截圖檔案結構
```
../Result_Screen_Shot/
├── 20250619_Mouse_Test_Result_1/          # 第 1 趟測試
│   ├── 20250619_Mouse_Test_1m_R1_143052.png
│   ├── 20250619_Mouse_Test_2m_R1_143127.png
│   ├── 20250619_Mouse_Test_3m_R1_143155.png
│   ├── 20250619_Mouse_Test_4m_R1_143223.png
│   └── 20250619_Mouse_Test_5m_R1_143251.png
├── 20250619_Mouse_Test_Result_2/          # 第 2 趟測試
│   ├── 20250619_Mouse_Test_1m_R2_150033.png
│   └── ...
└── 20250619_Mouse_Test_Result_3/          # 第 3 趟測試
    └── ...
```

## 🔮 未來擴展功能

### 轉盤系統整合 (規劃中)
- **多角度測試**: 支援 0°, 45°, 90°, 135°, 180° 角度測試
- **Arduino 步進馬達控制**: 精確角度定位
- **自動資料夾分類**: `Angle_0`, `Angle_45`, `Angle_90` 等
- **向下相容設計**: 現有程式無需修改

### 預期資料夾結構 (轉盤模式)
```
../Result_Screen_Shot/
├── 20250619_Mouse_Test_Angle_0/           # 0 度角測試
├── 20250619_Mouse_Test_Angle_45/          # 45 度角測試
├── 20250619_Mouse_Test_Angle_90/          # 90 度角測試
└── ...
```

## 🛠️ 故障排除

### 常見問題解決

#### HC-12 通訊失敗
```
症狀: 等待 Test_Start 超時
解決方案:
1. 檢查串口設定 (COM Port)
2. 重新插拔 Arduino 重置 HC-12
3. 確認電池電量充足
4. 使用 Debug.py 測試通訊
```

#### 截圖功能卡住
```
症狀: 程式在截圖階段停止回應
解決方案:
1. 刪除舊的 Result_Screen_Shot 資料夾
2. 確認磁碟空間充足
3. 檢查防毒軟體是否阻擋
4. 重新啟動程式
```

#### Sikuli 啟動失敗
```
症狀: 測試軟體無法開啟
解決方案:
1. ⚠️ 確認 sikulixide-2.0.5.jar 在 Mouse_U3_Auto_Test_Main/ 資料夾內
2. ⚠️ 確認 U3_Mouse_Test.sikuli/ 資料夾存在且在正確位置
3. 檢查 Java JDK 是否正確安裝 (java -version)
4. 手動測試: java -jar sikulixide-2.0.5.jar
5. 檢查檔案權限是否正確
```

#### 送餐機器人連線失敗
```
症狀: WebSocket 連線錯誤
解決方案:
1. 檢查機器人 IP 設定
2. 確認網路連線狀態
3. 重新啟動機器人系統
4. 測試 ping 連通性
```

### 緊急處理程序
```
1. 按 Ctrl+C 強制中斷程式
2. 重新插拔 Arduino 重置 HC-12
3. 檢查工作管理員關閉殘留的 java.exe
4. 清空 LOG 和截圖資料夾
5. 重新啟動測試程式
```

## 📈 系統效能

### 時間控制
- **單點測試時間**: 150 秒 (2.5 分鐘)
- **HC-12 通訊時間**: 通常 3-5 秒，最多 31 秒 (含重試)
- **實際測試時間**: 80 秒 (固定)
- **截圖處理時間**: 2-3 秒
- **剩餘緩衝時間**: 自動計算補足

### 可靠性設計
- **HC-12 重試機制**: 最多 2 次重試，每次 15 秒 timeout
- **通訊失敗處理**: 自動跳過失敗點，繼續下一個測試
- **時間同步控制**: Arduino 70秒 與 PC 80秒 並行執行
- **資源自動清理**: 程式結束時自動釋放所有資源

## 📚 程式架構

### 模組化設計
```
U3_Mouse_Auto_Test_Main.py     # 主控制程式
├── config.py                  # 設定檔管理
├── robot_ws_client.py         # 機器人 WebSocket 控制
├── serial_util.py             # HC-12 串口通訊
├── mouse_test_screenshot.py   # 截圖功能模組
└── log_util.py               # LOG 記錄系統
```

### 設計原則
- **非同步架構**: 使用 asyncio 提升效能
- **模組化開發**: 各功能獨立，便於維護
- **容錯設計**: 多層錯誤處理機制
- **向下相容**: 支援未來功能擴展

## 📋 版本歷史
- **v3.0** (2025-06-19) - 修復截圖模組檔案衝突問題，優化時間控制邏輯，支援多趟測試，改進路徑規劃
- **v2.0** (2025-06-18) - 加入 HC-12 通訊重試機制，統一訊息格式，提升通訊穩定性
- **v1.0** (2025-06-17) - 基礎功能實現，整合各模組，建立完整測試流程

## 👨‍💻 作者
**郭宇軒** - 自動化測試系統開發

專案開發歷程：三天時間從構想到實現，經過多次除錯與優化，最終實現穩定的無人化測試系統。

## 📄 授權聲明
本專案僅供學習研究使用，請勿用於商業用途。

## 🤝 貢獻指南
歡迎提出建議和改進方案：
1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/新功能`)
3. 提交變更 (`git commit -am '新增某功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 建立 Pull Request

## 📞 技術支援
如有技術問題或建議，請透過 GitHub Issues 聯繫。

---
*最後更新: 2025年6月24日*
