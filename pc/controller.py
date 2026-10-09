"""
=============================================================================
🎮 Universal ESP32 Motion Steering Controller & Fallback Bridge
=============================================================================
Supports:
  1. Direct Steering Angle Telemetry: DATA,<angle>,<nitro>,<brake>,<recal>
  2. 3-Axis Gyro Telemetry (Motion-Shooter Firmware): DATA,<gx>,<gy>,<gz>,<btn1>,<btn2>,<recal>
  3. Continuous Keyboard & Mouse Steering Fallbacks
"""

import math
import os
import sys
import threading
import time

import serial
import serial.tools.list_ports

from config import (
    DEFAULT_COM_PORT,
    GYRO_RATE_SENSITIVITY,
    INVERT_STEERING,
    SERIAL_BAUD,
    STEER_DEADZONE_DEG,
    STEER_MAX_ANGLE_DEG,
    STEER_SENSITIVITY,
    STEER_SMOOTHING,
)


class ControllerManager:
    """Manages ESP32 motion steering, gyro fusion, zero calibration, and keyboard/mouse."""

    def __init__(self, port=DEFAULT_COM_PORT, baud=SERIAL_BAUD):
        self.port = port
        self.baud = baud
        self.serial_conn = None
        self.running = True
        self.is_connected = False
        self.connection_info = "Searching for ESP32..."
        self.port_name = "None"

        # Tuning Parameters
        self.max_angle = STEER_MAX_ANGLE_DEG
        self.deadzone = STEER_DEADZONE_DEG
        self.smoothing = STEER_SMOOTHING
        self.sensitivity = STEER_SENSITIVITY
        self.invert = INVERT_STEERING

        # Software Zero-Center Offset
        self.center_offset_deg = 0.0

        # Dynamic Gyro Rate Integration State (for motion-shooter firmware)
        self._integrated_gyro_angle = 0.0
        self._gyro_bias_z = 0.0
        self._still_samples = 0
        self._last_gyro_time = time.time()

        # Filtered State (Thread-safe)
        self._raw_steer_angle = 0.0
        self._calibrated_angle = 0.0
        self._filtered_steer = 0.0       # Normalized [-1.0 to +1.0]
        self._nitro_down = False
        self._brake_down = False
        self._pov_toggle_requested = False
        self._recal_requested = False

        self._prev_nitro = False
        self._prev_brake = False
        self._lock = threading.Lock()

        # Keyboard Fallback Inputs
        self._kb_steer = 0.0
        self._kb_nitro = False
        self._kb_brake = False
        self._kb_pov_toggle = False

        # Background Serial Worker
        self.thread = threading.Thread(target=self._serial_worker, daemon=True)
        self.thread.start()

    def calibrate_center(self):
        """Zero the steering angle at the current position."""
        with self._lock:
            self.center_offset_deg = self._raw_steer_angle
            self._integrated_gyro_angle = 0.0
            self._calibrated_angle = 0.0
            self._filtered_steer = 0.0
            self._recal_requested = True
        self.send_recalibrate_to_esp()

    def send_recalibrate_to_esp(self):
        if self.is_connected and self.serial_conn:
            try:
                self.serial_conn.write(b"RECAL\n")
            except Exception:
                pass

    def _find_esp32_port(self):
        ports = serial.tools.list_ports.comports()
        keywords = ["CP210", "CH340", "USB-SERIAL", "ESP32", "UART", "USB Serial", "Silicon Labs", "FTDI", "Arduino"]
        for p in ports:
            desc = f"{p.description} {p.manufacturer or ''} {p.hwid or ''}".lower()
            for kw in keywords:
                if kw.lower() in desc:
                    return p.device
        if ports:
            return ports[0].device
        return None

    def _serial_worker(self):
        buffer_str = ""
        while self.running:
            if not self.is_connected:
                target_port = self.port or self._find_esp32_port()
                if target_port and self.running:
                    try:
                        self.serial_conn = serial.Serial(
                            target_port,
                            self.baud,
                            timeout=0.02,
                            write_timeout=0.2
                        )
                        try:
                            self.serial_conn.dtr = False
                            self.serial_conn.rts = False
                        except Exception:
                            pass
                        time.sleep(0.15)
                        self.serial_conn.reset_input_buffer()
                        self.is_connected = True
                        self.port_name = target_port
                        self.connection_info = f"ESP32: {target_port} (115200)"
                    except Exception as e:
                        self.is_connected = False
                        self.connection_info = "Keyboard / Mouse Mode"
                        time.sleep(1.0)
                else:
                    self.connection_info = "Keyboard / Mouse Mode"
                    time.sleep(1.2)
                continue

            try:
                raw_bytes = self.serial_conn.read(128)
                if raw_bytes:
                    buffer_str += raw_bytes.decode("ascii", errors="ignore")
                    while "\n" in buffer_str:
                        line, buffer_str = buffer_str.split("\n", 1)
                        line = line.strip()
                        if line:
                            self._parse_line(line)
                else:
                    time.sleep(0.005)
            except (serial.SerialException, OSError):
                self.is_connected = False
                self.connection_info = "ESP32 Disconnected"
                if self.serial_conn:
                    try:
                        self.serial_conn.close()
                    except Exception:
                        pass
                    self.serial_conn = None
                time.sleep(0.8)

    def _parse_line(self, line: str):
        """
        Parses incoming serial stream.
        Format A (Direct Angle): DATA,<angle>,<nitro>,<brake>,<recal>
        Format B (3-Axis Gyro):  DATA,<gx>,<gy>,<gz>,<btn1>,<btn2>,<recal>
        """
        if not line.startswith("DATA,"):
            if "CALIBRATION_COMPLETE" in line:
                with self._lock:
                    self._recal_requested = True
            return

        parts = line.split(",")
        num_parts = len(parts)

        now = time.time()
        dt = max(0.001, min(0.05, now - self._last_gyro_time))
        self._last_gyro_time = now

        # Case 1: 3-Axis Gyro Stream from motion-shooter firmware (>= 6 parts with float values)
        if num_parts >= 6:
            try:
                val1 = float(parts[1])
                val2 = float(parts[2])
                val3 = float(parts[3])
                btn1 = int(parts[4]) == 1
                btn2 = int(parts[5]) == 1 if num_parts >= 7 else False
                recal = int(parts[6]) == 1 if num_parts >= 7 else False

                # Gyro Z or X rotation (steering wheel turn)
                # Auto-detect primary steering rotation axis (Z or X)
                gyro_rot = val3 if abs(val3) > abs(val1) else val1

                # Zero drift auto-compensation when stationary
                if abs(gyro_rot - self._gyro_bias_z) < 1.0:
                    self._still_samples += 1
                    if self._still_samples > 15:
                        self._gyro_bias_z += (gyro_rot - self._gyro_bias_z) * 0.03
                else:
                    self._still_samples = 0

                corr_rate = gyro_rot - self._gyro_bias_z
                # Integrate gyro angular velocity to get continuous tilt angle
                self._integrated_gyro_angle += corr_rate * dt * GYRO_RATE_SENSITIVITY * 45.0
                # Gentle natural centering decay
                self._integrated_gyro_angle *= 0.985
                self._integrated_gyro_angle = max(-60.0, min(60.0, self._integrated_gyro_angle))

                raw_angle = self._integrated_gyro_angle
                self._process_steering_angle(raw_angle, btn1, btn2, recal)
                return
            except (ValueError, IndexError):
                pass

        # Case 2: Direct Tilt Angle (5 parts: DATA,angle,nitro,brake,recal)
        if num_parts >= 5:
            try:
                raw_angle = float(parts[1])
                nitro = int(parts[2]) == 1
                brake = int(parts[3]) == 1
                recal = int(parts[4]) == 1
                self._process_steering_angle(raw_angle, nitro, brake, recal)
            except (ValueError, IndexError):
                pass

    def _process_steering_angle(self, raw_angle: float, nitro: bool, brake: bool, recal: bool):
        """Applies deadzone, calibration offset, sensitivity, and smoothing."""
        with self._lock:
            self._raw_steer_angle = raw_angle
            cal_angle = raw_angle - self.center_offset_deg
            self._calibrated_angle = cal_angle

            # Deadzone
            angle = cal_angle
            if abs(angle) < self.deadzone:
                angle = 0.0
            else:
                sign = 1.0 if angle > 0 else -1.0
                angle = sign * (abs(angle) - self.deadzone)

            # Normalize to [-1.0, 1.0]
            span = max(5.0, self.max_angle - self.deadzone)
            norm_steer = (angle / span) * self.sensitivity
            norm_steer = max(-1.0, min(1.0, norm_steer))
            if self.invert:
                norm_steer = -norm_steer

            # EMA Smoothing filter
            self._filtered_steer = (
                (1.0 - self.smoothing) * norm_steer
                + self.smoothing * self._filtered_steer
            )

            # Button triggers
            if brake and not self._prev_brake:
                self._pov_toggle_requested = True

            self._nitro_down = nitro
            self._brake_down = brake
            self._prev_nitro = nitro
            self._prev_brake = brake

            if recal:
                self.center_offset_deg = raw_angle
                self._calibrated_angle = 0.0
                self._filtered_steer = 0.0
                self._recal_requested = True

    def update_fallback_inputs(self, steer_axis: float, nitro: bool, brake: bool, pov_toggle: bool):
        """Feeds keyboard and mouse steering inputs."""
        with self._lock:
            self._kb_steer = steer_axis
            self._kb_nitro = nitro
            self._kb_brake = brake
            if pov_toggle:
                self._kb_pov_toggle = True

    def get_frame_input(self):
        """
        Returns: (steer_axis [-1..1], nitro, brake, pov_toggle, recal, cal_deg, raw_deg)
        """
        with self._lock:
            # If ESP32 is connected and actively sending tilt, use it; else use keyboard
            if self.is_connected and abs(self._raw_steer_angle) > 0.05:
                # Merge hardware with keyboard so user can use either at any time
                steer = self._filtered_steer if abs(self._kb_steer) < 0.05 else self._kb_steer
                nitro = self._nitro_down or self._kb_nitro
                brake = self._brake_down or self._kb_brake
                cal_deg = self._calibrated_angle if abs(self._kb_steer) < 0.05 else (self._kb_steer * self.max_angle)
                raw_deg = self._raw_steer_angle
            else:
                steer = self._kb_steer
                nitro = self._kb_nitro
                brake = self._kb_brake
                cal_deg = self._kb_steer * self.max_angle
                raw_deg = cal_deg

            pov_toggle = self._pov_toggle_requested or self._kb_pov_toggle
            recal = self._recal_requested

            self._pov_toggle_requested = False
            self._kb_pov_toggle = False
            self._recal_requested = False

            return steer, nitro, brake, pov_toggle, recal, cal_deg, raw_deg

    def shutdown(self):
        self.running = False
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        self.thread.join(timeout=0.5)
