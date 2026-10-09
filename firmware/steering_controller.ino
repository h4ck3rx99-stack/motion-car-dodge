/*
  =============================================================================
  🏎️ ESP32 + MPU6050 Motion Steering Controller for Highway Car Dodger
  =============================================================================
  Streams real-time steering tilt angle and button inputs over USB Serial (115200 baud).

  Hardware Wiring:
    - MPU6050 VCC -> ESP32 3.3V (or 5V if 5V tolerant board)
    - MPU6050 GND -> ESP32 GND
    - MPU6050 SCL -> ESP32 GPIO 22 (I2C Clock)
    - MPU6050 SDA -> ESP32 GPIO 21 (I2C Data)
    - Button 1 (Nitro / Boost) -> ESP32 GPIO 18 & GND (Internal pull-up)
    - Button 2 (Brake / POV Toggle) -> ESP32 GPIO 19 & GND (Internal pull-up)
      (Hold Button 2 for > 1.5s to recalibrate steering center)

  Telemetry Protocol:
    DATA,<steer_angle_deg>,<nitro_state>,<brake_state>,<recal_event>
    Example: "DATA,-14.25,0,0,0" (tilted 14.25 degrees left)
  =============================================================================
*/

#include <Wire.h>

#define I2C_SDA 21
#define I2C_SCL 22
#define MPU6050_ADDR 0x68

#define PIN_NITRO_BTN 18     // Button 1 (Nitro Boost)
#define PIN_BRAKE_BTN 19     // Button 2 (Brake / Camera POV Toggle 'V')
#define PIN_STATUS_LED 2     // Onboard Blue Status LED

float steerAngle = 0.0f;
float gyroOffsetX = 0.0f;
float gyroOffsetY = 0.0f;
float gyroOffsetZ = 0.0f;
float accelOffsetAngle = 0.0f;

unsigned long prevTimeMicros = 0;
unsigned long lastTelemetryMs = 0;
const int TELEMETRY_INTERVAL_MS = 10; // 100 Hz output rate

unsigned long brakePressStart = 0;
bool recalibrating = false;

void writeMPU(uint8_t reg, uint8_t data) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(reg);
  Wire.write(data);
  Wire.endTransmission(true);
}

void readMPURaw(int16_t &ax, int16_t &ay, int16_t &az, int16_t &gx, int16_t &gy, int16_t &gz) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)MPU6050_ADDR, (uint8_t)14, (uint8_t)true);

  if (Wire.available() >= 14) {
    ax = (Wire.read() << 8) | Wire.read();
    ay = (Wire.read() << 8) | Wire.read();
    az = (Wire.read() << 8) | Wire.read();
    Wire.read(); Wire.read(); // Skip temperature bytes
    gx = (Wire.read() << 8) | Wire.read();
    gy = (Wire.read() << 8) | Wire.read();
    gz = (Wire.read() << 8) | Wire.read();
  }
}

void calibrateSensors() {
  digitalWrite(PIN_STATUS_LED, HIGH);
  Serial.println("STATUS:CALIBRATING_DO_NOT_MOVE");

  long sumGx = 0, sumGy = 0, sumGz = 0;
  long sumAx = 0, sumAy = 0, sumAz = 0;
  const int samples = 150;

  for (int i = 0; i < samples; i++) {
    int16_t ax, ay, az, gx, gy, gz;
    readMPURaw(ax, ay, az, gx, gy, gz);
    sumGx += gx;
    sumGy += gy;
    sumGz += gz;
    sumAx += ax;
    sumAy += ay;
    sumAz += az;
    delay(5);
  }

  gyroOffsetX = (float)sumGx / samples;
  gyroOffsetY = (float)sumGy / samples;
  gyroOffsetZ = (float)sumGz / samples;

  float avgAy = (float)sumAy / samples;
  float avgAz = (float)sumAz / samples;
  accelOffsetAngle = atan2(avgAy, avgAz) * (180.0f / PI);
  steerAngle = 0.0f;

  digitalWrite(PIN_STATUS_LED, LOW);
  Serial.println("STATUS:CALIBRATION_COMPLETE");
}

void setup() {
  Serial.begin(115200);
  delay(150);

  pinMode(PIN_NITRO_BTN, INPUT_PULLUP);
  pinMode(PIN_BRAKE_BTN, INPUT_PULLUP);
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, LOW);

  Wire.begin(I2C_SDA, I2C_SCL, 400000);
  delay(100);

  writeMPU(0x6B, 0x00); // Wake up MPU
  delay(50);
  writeMPU(0x1B, 0x08); // Gyro +/- 500 dps
  writeMPU(0x1C, 0x08); // Accel +/- 4g
  writeMPU(0x1A, 0x03); // DLPF ~42Hz

  calibrateSensors();
  prevTimeMicros = micros();
}

void loop() {
  unsigned long nowMicros = micros();
  float dt = (nowMicros - prevTimeMicros) / 1000000.0f;
  prevTimeMicros = nowMicros;
  if (dt <= 0.0f || dt > 0.1f) dt = 0.01f;

  int16_t rawAx, rawAy, rawAz, rawGx, rawGy, rawGz;
  readMPURaw(rawAx, rawAy, rawAz, rawGx, rawGy, rawGz);

  // Measure both roll (X) and yaw (Z) so steering works regardless of how breadboard is held
  float gyroRateRoll = ((float)rawGx - gyroOffsetX) / 65.5f;
  float gyroRateYaw = ((float)rawGz - gyroOffsetZ) / 65.5f;

  float activeGyroRate = abs(gyroRateRoll) > abs(gyroRateYaw) ? gyroRateRoll : gyroRateYaw;

  float accelAngle = (atan2((float)rawAy, (float)rawAz) * (180.0f / PI)) - accelOffsetAngle;

  const float alpha = 0.96f;
  steerAngle = alpha * (steerAngle + activeGyroRate * dt) + (1.0f - alpha) * accelAngle;

  if (steerAngle < -75.0f) steerAngle = -75.0f;
  if (steerAngle > 75.0f) steerAngle = 75.0f;

  bool nitroPressed = (digitalRead(PIN_NITRO_BTN) == LOW);
  bool brakePressed = (digitalRead(PIN_BRAKE_BTN) == LOW);

  int recalEvent = 0;
  if (brakePressed) {
    if (brakePressStart == 0) {
      brakePressStart = millis();
    } else if (millis() - brakePressStart > 1500 && !recalibrating) {
      recalibrating = true;
      steerAngle = 0.0f;
      calibrateSensors();
      recalEvent = 1;
    }
  } else {
    brakePressStart = 0;
    recalibrating = false;
  }

  if (nitroPressed || brakePressed || recalibrating) {
    digitalWrite(PIN_STATUS_LED, HIGH);
  } else {
    digitalWrite(PIN_STATUS_LED, LOW);
  }

  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "RECAL" || cmd == "RESET") {
      calibrateSensors();
      recalEvent = 1;
    }
  }

  unsigned long nowMs = millis();
  if (nowMs - lastTelemetryMs >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryMs = nowMs;

    // Send DATA,<steer>,<nitro>,<brake>,<recal>
    Serial.print("DATA,");
    Serial.print(steerAngle, 2);
    Serial.print(",");
    Serial.print(nitroPressed ? 1 : 0);
    Serial.print(",");
    Serial.print(brakePressed ? 1 : 0);
    Serial.print(",");
    Serial.println(recalEvent);
  }
}
