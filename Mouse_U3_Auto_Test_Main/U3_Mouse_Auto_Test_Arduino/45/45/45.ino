#include <Stepper.h>


// 定義步進馬達每轉的步數
// (例如：對於 1.8 度/步的馬達，通常是 200 步)
const int stepsPerRevolution = 2048;

// 初始化 Stepper 函式庫，設定在 pin 8, 9, 10, 11:
// (請根據你的步進馬達驅動板的接線調整這些針腳)
Stepper myStepper(stepsPerRevolution, 8, 10, 9, 11);

void setup() {
  // 設定馬達轉速，單位為 RPM (每分鐘轉數)
  myStepper.setSpeed(3); // 60 RPM -> 24 RPM 輪盤降速 改善輪盤至定點後的慣性回移
  Serial.begin(9600);     // 啟動序列通訊
  Serial.println("Arduino 已準備好。等待指令 (例如: ROTATE_DEGREE:90)...");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n'); // 讀取直到換行符號的 incoming 指令
    command.trim(); // 移除任何空白字元

    // 檢查指令是否以 "ROTATE_DEGREE:" 開頭
    if (command.startsWith("ROTATE_DEGREE:")) {
      // 提取度數部分
      String degreeString = command.substring(command.indexOf(':') + 1);
      int degrees = degreeString.toInt(); // 將字串轉換為整數

      if (degrees != 0 || degreeString == "0") { // 確保轉換成功或輸入為0
        // 計算所需步數： (每轉步數 / 360) * 度數
        int stepsToRotate = (stepsPerRevolution / 360.0) * degrees;
        Serial.print("正在旋轉 ");
        Serial.print(degrees);
        Serial.print(" 度 (共 ");
        Serial.print(stepsToRotate);
        Serial.println(" 步)...");
        myStepper.step(stepsToRotate);
        Serial.println("旋轉完成。");
      } else {
        Serial.println("無效的度數。請輸入一個數字。");
      }
    } else {
      Serial.println("未知指令。");
    }
  }
}