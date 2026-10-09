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
    - Button 1 (Nitro/Boost) -> ESP32 GPIO 18 & GND (Internal pull-up)
    - Button 2 (Brake/Cam POV) -> ESP32 GPIO 19 & GND (Internal pull-up)
      (Hold Button 2 for > 1.5 seconds to zero/recalibrate steering center)

  Telemetry Protocol:
    DATA,<steer_angle_deg>,<nitro_state>,<brake_state>,<recal_event>
    Example: "DATA,-14.25,0,0,0" (tilted 14.25 degrees left)
  =============================================================================
*/

#include <Wire.h>

// I2C Pins & MPU Address
#define I2C_SDA 21
#define I2C_SCL 22
#define MPU6050_ADDR 0x68

// Pushbuttons & LED
#define PIN_NITRO_BTN 18     // Button 1 (Nitro Boost / Horn)
#define PIN_BRAKE_BTN 19     // Button 2 (Brake / Camera POV Toggle)
#define PIN_STATUS_LED 2     // Onboard Status Blue LED

// Sensor Calibration & Complementary Filter
float steerAngle = 0.0f;       // Filtered steering angle in degrees (-90 to +90)
float gyroOffsetZ = 0.0f;
float gyroOffsetY = 0.0f;
float gyroOffsetX = 0.0f;
float accelOffsetAngle = 0.0f;

// Calibration & Loop Timing
unsigned long prevTimeMicros = 0;
unsigned long lastTelemetryMs = 0;
const int TELEMETRY_INTERVAL_MS = 10; // 100 Hz output rate

// Button State Tracking
bool prevNitroState = HIGH;
bool prevBrakeState = HIGH;
unsigned long brakePressStart = 0;
bool recalibrating = false;

// ----------------------------------------------------------------------------
// MPU6050 Low-Level Helper Functions
// ----------------------------------------------------------------------------
void writeMPU(uint8_t reg, uint8_t data) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(reg);
  Wire.write(data);
  Wire.endTransmission(true);
}

void readMPURaw(int16_t &ax, int16_t &ay, int16_t &az, int16_t &gx, int16_t &gy, int16_t &gz) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B); // Starting register for Accel X High
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
  const int samples = 200;

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
  // Calculate initial roll angle from gravity vector
  accelOffsetAngle = atan2(avgAy, avgAz) * (180.0f / PI);
  steerAngle = 0.0f;

  digitalWrite(PIN_STATUS_LED, LOW);
  Serial.println("STATUS:CALIBRATION_COMPLETE");
}

void setup() {
  Serial.begin(115200);
  delay(200);

  // Setup I/O
  pinMode(PIN_NITRO_BTN, INPUT_PULLUP);
  pinMode(PIN_BRAKE_BTN, INPUT_PULLUP);
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, LOW);

  // Initialize I2C (400kHz Fast Mode)
  Wire.begin(I2C_SDA, I2C_SCL, 400000);
  delay(100);

  // Wake up MPU6050 (clear sleep bit)
  writeMPU(0x6B, 0x00);
  delay(50);
  // Configure Gyro Full Scale Range (+/- 500 deg/s)
  writeMPU(0x1B, 0x08);
  // Configure Accel Full Scale Range (+/- 4g)
  writeMPU(0x1C, 0x08);
  // Configure Digital Low Pass Filter (DLPF ~ 42Hz)
  writeMPU(0x1A, 0x03);

  calibrateSensors();
  prevTimeMicros = micros();
}

void loop() {
  unsigned long nowMicros = micros();
  float dt = (nowMicros - prevTimeMicros) / 1000000.0f;
  prevTimeMicros = nowMicros;
  if (dt <= 0.0f || dt > 0.1f) dt = 0.01f; // Safeguard against timer roll-overs

  // Read raw sensor values
  int16_t rawAx, rawAy, rawAz, rawGx, rawGy, rawGz;
  readMPURaw(rawAx, rawAy, rawAz, rawGx, rawGy, rawGz);

  // Gyro deg/sec (Sensitivity at +/- 500 dps is 65.5 LSB/(deg/s))
  // When holding the board as a steering wheel, tilting left/right is Roll around X-axis or Y-axis
  float gyroRateRoll = ((float)rawGx - gyroOffsetX) / 65.5f;

  // Accel Roll Angle from gravity (degrees)
  // atan2(Ay, Az) gives roll inclination
  float accelAngle = (atan2((float)rawAy, (float)rawAz) * (180.0f / PI)) - accelOffsetAngle;

  // Complementary Filter: 96% Gyro Integration + 4% Accelerometer Drift Correction
  const float alpha = 0.96f;
  steerAngle = alpha * (steerAngle + gyroRateRoll * dt) + (1.0f - alpha) * accelAngle;

  // Clamp steering angle to [-75, +75] degrees
  if (steerAngle < -75.0f) steerAngle = -75.0f;
  if (steerAngle > 75.0f) steerAngle = 75.0f;

  // Read pushbuttons (Active LOW)
  bool nitroPressed = (digitalRead(PIN_NITRO_BTN) == LOW);
  bool brakePressed = (digitalRead(PIN_BRAKE_BTN) == LOW);

  // Check for Long-Press Brake button to recalibrate center
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

  // Visual status LED indicator
  if (nitroPressed || brakePressed || recalibrating) {
    digitalWrite(PIN_STATUS_LED, HIGH);
  } else {
    digitalWrite(PIN_STATUS_LED, LOW);
  }

  // Handle incoming Serial commands from PC (e.g. "RECAL")
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "RECAL" || cmd == "RESET") {
      calibrateSensors();
      recalEvent = 1;
    }
  }

  // Send 100Hz Telemetry Stream
  unsigned long nowMs = millis();
  if (nowMs - lastTelemetryMs >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryMs = nowMs;

    // Protocol: DATA,<steer_angle>,<nitro>,<brake>,<recal>
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
