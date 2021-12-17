
#include <Encoder.h>

Encoder slide(3, 2);
Encoder joint_0(21, 20);
Encoder joint_1(19, 18);

void setup() {
  Serial.begin(9600);
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
float time_diff = 0;
void loop() {
  current_time = millis();
  time_diff = (current_time - prev_time)/1000.0;
  slide_pos = slide.read()/464.64 * 0.04;
  joint_0_pos = angleWrap(M_PI * 2 * joint_0.read() / 2400.0 + M_PI);
  joint_1_pos = angleWrap(M_PI * 2 * joint_1.read() / 2400.0);

  slide_pos_dot = slide_pos - slide_pos_prev / time_diff;
  joint_0_pos_dot = (joint_0_pos - joint_0_pos_prev) / time_diff;
  joint_1_pos_dot = (joint_1_pos - joint_1_pos_prev) / time_diff;

  Serial.print(slide_pos,7);
  Serial.print(",");
  Serial.print(joint_0_pos,7);
  Serial.print(",");
  Serial.print(joint_1_pos,7);
  Serial.print(",");
  Serial.print(slide_pos_dot,7);
  Serial.print(",");
  Serial.print(joint_0_pos_dot,7);
  Serial.print(",");
  Serial.println(joint_1_pos_dot,7);
  slide_pos_prev = slide_pos;
  joint_0_pos_prev = joint_0_pos;
  joint_1_pos_prev = joint_1_pos;
  prev_time = current_time;
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
