// ======================================
// Arduino 四驅循跡最終穩定版
// 前進一下停一下 + 單邊修正 + 立即終點停
// ======================================

int sensorLeft  = A0;
int sensorRight = A2;
int threshold   = 250;

// 左側 L298N
int ENA = 5;  int IN1 = 6;  int IN2 = 7;
// 右側 L298N
int ENB = 10; int IN3 = 8; int IN4 = 9;

// === 速度參數 ===
int forwardSpeed = 75;       // 前進速度（不宜太快）
int adjustSpeed  = 85;       // 修正時單邊輪速度
int moveTime     = 60;       // 每次推進時間（短距離）
int adjustTime   = 150;      // 修正停留時間
int smoothPush   = 40;       // 修正後補推時間

int fullBlackCount = 0;
int fullBlackThreshold = 2;

void setup() {
  Serial.begin(9600);
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
}

void loop() {
  int L = analogRead(sensorLeft);
  int R = analogRead(sensorRight);
  bool l = L > threshold;
  bool r = R > threshold;

  Serial.print("L: "); Serial.print(L);
  Serial.print(" | R: "); Serial.print(R);
  Serial.print(" || ");

  // 終點判斷放最前，避免衝太遠
  if (l && r) {
    fullBlackCount++;
    Serial.print("全黑第 "); Serial.print(fullBlackCount); Serial.println(" 次");

    if (fullBlackCount >= fullBlackThreshold) {
      Serial.println("🎯 抵達終點，停車觀察");
      stopAll();
      delay(1000);
      fullBlackCount = 0;
    } else {
      stopAll(); delay(50);
    }
  }

  else if (!l && !r) {
    Serial.println("✔ 線中 ➜ 前進");
    moveForward();
    fullBlackCount = 0;
  }

  else if (l && !r) {
    Serial.println("偏左 ➜ 修右輪");
    rightWheelAdjust();
    smoothForward();
    fullBlackCount = 0;
  }

  else if (!l && r) {
    Serial.println("偏右 ➜ 修左輪");
    leftWheelAdjust();
    smoothForward();
    fullBlackCount = 0;
  }

  else {
    Serial.println("❓未知狀態 ➜ 停止保護");
    stopAll(); delay(50);
    fullBlackCount = 0;
  }

  delay(10);
}

// === 動作區 ===

void moveForward() {
  setMotors(forwardSpeed, forwardSpeed);
  delay(moveTime);
  stopAll(); delay(20);
}

void smoothForward() {
  setMotors(forwardSpeed, forwardSpeed);
  delay(smoothPush);
  stopAll(); delay(20);
}

void leftWheelAdjust() {
  analogWrite(ENA, adjustSpeed);
  analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(adjustTime);
  stopAll(); delay(20);
}

void rightWheelAdjust() {
  analogWrite(ENA, 0);
  analogWrite(ENB, adjustSpeed);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  delay(adjustTime);
  stopAll(); delay(20);
}

void stopAll() {
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

void setMotors(int leftPWM, int rightPWM) {
  analogWrite(ENA, leftPWM);
  analogWrite(ENB, rightPWM);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}
