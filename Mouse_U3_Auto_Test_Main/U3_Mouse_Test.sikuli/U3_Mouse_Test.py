# 滑鼠U3測試
# === 以此資料夾相對路徑呼叫 Primax 測試程式 ===
primax_test_tool_path = os.path.join(getBundlePath(), "../PrimaxMouseTest.exe")
App.open(primax_test_tool_path)
wait(2)

# 將Primax Test Tool最大化
type(Key.UP, KeyModifier.WIN)
wait(1)

# 嘗試點選功能選單(Distance Test)
if exists(Pattern("Functions_Menu.png").targetOffset(44,-1), 5):
    wait(0.2)
    print("[Sikuli] Click Functions Menu...")
    wait(0.2)
    click(Pattern("Functions_Menu.png").targetOffset(43,0))
    wait(1)
    if exists(Pattern("Select_ReportRate_Test.png").targetOffset(-8,-1), 5):
        wait(0.2)
        print("[Sikuli] Select 'ReportRate Test'")
        wait(0.2)
        click(Pattern("Select_ReportRate_Test.png").targetOffset(-8,-1))
        wait(0.5)
        if exists(Pattern("Time_Set_Menu.png").targetOffset(18,-3),5):
            wait(0.2)
            print("[Sikuli] Click Time Set Menu...")
            wait(0.2)
            click(Pattern("Time_Set_Menu.png").targetOffset(18,-3))
            wait(1)
            if exists(Pattern("Select_Time_Set.png").targetOffset(-7,-48),5):
                wait(0.2)
                print("[Sikuli] Select '1 min.'")
                wait(0.2)
                click(Pattern("Select_Time_Set.png").targetOffset(-7,-48))
                wait(0.5)
                if exists(Pattern("ReportRate_Threshold_Set.png").targetOffset(27,-1),5):
                    doubleClick(Pattern("ReportRate_Threshold_Set.png").targetOffset(27,-1))
                    wait(0.5)
                    print("[Sikuli] Set ReportRate Threshold To '100' ")
                    wait(0.2)
                    type("100")
                    wait(0.5)
                    print("[Sikuli] Primax Tool Launched Done.")
                else:
                    print("[Sikuli] ERROR: 'Threshold Set' Not Found. Exiting...")
                    exit()
            else:
                print("[Sikuli] ERROR: '1 min.' Item In Time Set Menu Not Found. Exiting...")
                exit()
        else:
            print("[Sikuli] ERROR: Time Set Menu Not Found. Exiting...")
            exit()
    else:
        print("[Sikuli] ERROR: 'ReportRate Test' Item In Functions Menu Not Found. Exiting...")
        exit()
else:
    print("[Sikuli] ERROR: Main Functions Menu Not Found. Exiting...")
    exit()
