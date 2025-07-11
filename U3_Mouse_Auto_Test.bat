@echo off
:: ► 切換到本 .bat 所在資料夾
cd /d "%~dp0"

:: ► 進入 Main 資料夾
cd Mouse_U3_Auto_Test_Main

:: ► 執行主程式
python U3_Mouse_Auto_Test_Main_Turntable.py

:: ► 執行完後暫停，避免視窗瞬間關閉
pause
