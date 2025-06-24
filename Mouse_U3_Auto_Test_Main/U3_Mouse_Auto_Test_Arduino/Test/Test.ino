#include <SoftwareSerial.h>
SoftwareSerial hc12(2, 3);

const int relayPin = 7;
const int ledPin = 13; // 你可以換成你接的 LED 腳位

void setup() {
  hc12.begin(9600);
  pinMode(relayPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  digitalWrite(relayPin, HIGH);  // 初始化為關閉（HIGH = 關閉）
  digitalWrite(ledPin, LOW);     // LED 預設熄滅
}

void loop() {
  if (hc12.available()) {
    String received = hc12.readString();
    received.trim();
    
    if (received == "Robot_Arrived") {
      // 🟡 狀態提示：快速閃爍 3 次
      for (int i = 0; i < 3; i++) {
        digitalWrite(ledPin, HIGH);
        delay(200);
        digitalWrite(ledPin, LOW);
        delay(200);
      }

      // ✅ 啟動狀態：長亮 LED，啟動繼電器
      digitalWrite(ledPin, HIGH);
      digitalWrite(relayPin, LOW);     // 啟動繼電器（滾輪開始轉）
      delay(1500);                     // 緩衝時間
      hc12.println("Test_Start");      // 回傳開始訊號

      delay(70000);                    // 滾輪作動 70 秒
      digitalWrite(relayPin, HIGH);    // 關閉繼電器
      hc12.println("Relay_End");       // optional 通知主機

      // ⛔️ 收尾：LED 熄滅
      digitalWrite(ledPin, LOW);
    }
  }
}
