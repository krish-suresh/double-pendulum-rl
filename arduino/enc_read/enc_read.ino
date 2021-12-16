
#include <Encoder.h>
#include <JrkG2.h>

Encoder slide(7, 8);
Encoder joint_0(11, 12);
Encoder joint_1(10, 9);
JrkG2I2C jrk;

void setup() {
  Serial.begin(9600);
  Wire.begin();
}

float slide_pos = 0;
float joint_0_pos = 0;
float joint_1_pos = 0;
float slide_pos_prev = 0;
float joint_0_pos_prev = 0;
float joint_1_pos_prev = 0;
float slide_pos_dot = 0;
float joint_0_pos_dot = 0;
float joint_1_pos_dot = 0;
int current_time = 0;
int prev_time = 0;
int time_diff = 0;
void loop() {
  current_time = millis();
  time_diff = current_time - prev_time;
  slide_pos = joint_0.read();
  joint_0_pos = angleWrap(M_PI * 2 * joint_0.read() / 2400.0 + M_PI);
  joint_1_pos = angleWrap(M_PI * 2 * joint_1.read() / 2400.0 + M_PI);

  slide_pos_dot = slide_pos - slide_pos_prev / time_diff;
  joint_0_pos_dot = joint_0_pos - joint_0_pos_prev / time_diff;
  joint_1_pos_dot = joint_1_pos - joint_1_pos_prev / time_diff;

  Serial.print(slide_pos);
  Serial.print(",");
  Serial.print(joint_0_pos);
  Serial.print(",");
  Serial.print(joint_1_pos);
  Serial.print(slide_pos_dot);
  Serial.print(",");
  Serial.print(joint_0_pos_dot);
  Serial.print(",");
  Serial.println(joint_1_pos_dot);

  if (Serial.available() > 0) {
    float power = Serial.parseInt();
    setMotor(power);
  }

  slide_pos_prev = slide_pos;
  joint_0_pos_prev = joint_0_pos;
  joint_1_pos_prev = joint_1_pos;
  prev_time = current_time;
}

void stopMotor() {
  setMotor(0);
}

void setMotor(float power) {
  jrk.setTarget(2048.0 * (power + 1));
}

float angleWrap(float angle) {
  while (angle < -M_PI) {
    angle += 2 * M_PI  ;
  }
  while (angle > M_PI) {
    angle -= 2 * M_PI  ;
  }
  return angle;
}
