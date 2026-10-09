# 🏁 OUTDRIVE 1992 - 1990s 2D Arcade Driver POV Highway Racer

A lost **1990s arcade racing cabinet** experience viewed from the **driver's POV**, built with **2D pixel art, pseudo-3D raster scanning, realistic lane traffic, and dynamic traffic waves** on retro hardware aesthetics.

Powered by physical motion steering with an **ESP32 + MPU6050** (with instantaneous keyboard and mouse fallbacks).

---

## 🎮 Key Features & Mechanics

1. **🛣️ Right-Hand Drive Highway & Lane System**:
   - **Right Lanes (Lanes 2 & 3)**: Where the player drives! Traffic drives forward in the same direction at moderate cruising speeds with taillights showing.
   - **Left Lanes (Lanes 0 & 1)**: Oncoming traffic heading toward you with headlights on.
2. **🔭 Increased Render Distance & Distant Spawning**:
   - `DRAW_DISTANCE` increased to **220 segments** for expansive horizon visibility.
   - Cars and fuel cans spawn **far on the distant horizon (2,200 to 6,200 units ahead)** so you have plenty of time to see them approaching and plan your lane changes.
3. **⏱️ Balanced & Readable Speed**:
   - Cruise and top speeds have been tuned to comfortable, readable retro arcade speeds (45–115 MPH, 160 MPH Nitro).
4. **🌊 Dynamic Traffic Density Waves**:
   - Traffic count oscillates in a **36-second rhythmic wave** (from gentle cruising to rush hour surges and back).
5. **⛽ Infinite Road Fuel & Powerups**:
   - High-contrast red **Fuel Jerry Cans** spawn continuously in highway lanes ahead of you.
   - Steer into fuel cans to restore **+35% Fuel** and keep your run alive forever!
6. **🏎️ Driver's POV Interior Cockpit**:
   - Windshield framing with dark A-pillars and rear-view mirror.
   - 2D pixel dashboard with analog speedometer needle, digital gear indicator (`LO` / `HI`), and fuel gauge.
   - **Animated 2D Pixel Steering Wheel** that rotates in real-time matching physical ESP32 tilt.
7. **🌈 5 Switchable 1990s Themes (Press `'T'` to cycle)**:
   - **Sunny Countryside**: Vibrant blue banded sky, green grass, pine trees, farmhouses.
   - **Sunset Highway**: Warm orange/purple/magenta sunset, glowing sun, mountain silhouettes.
   - **Night Runner**: Indigo sky, streetlights, glowing city skyline, headlights.
   - **Storm Drift**: Slate overcast sky, rain streaks, reflective asphalt.
   - **City Outskirts**: Industrial warehouses, billboards, gas stations, urban skyline.
8. **📺 Optional CRT Monitor Scanlines (Press `'C'` to toggle)**:
   - Authentic 1990s arcade CRT monitor scanlines.

---

## 🔌 Hardware Wiring Guide

```text
MPU6050 Pin   ->   ESP32 Pin
----------------------------
VCC           ->   3.3V
GND           ->   GND
SCL           ->   GPIO 22
SDA           ->   GPIO 21

Buttons:
Button 1 (Turbo Boost)          -> GPIO 18 & GND
Button 2 (Brake / Cam POV 'V')  -> GPIO 19 & GND  (Hold > 1.5s to recalibrate)
```

---

## 🚀 How to Run

```powershell
cd "c:\X Drive\GGame\motion-car-dodge"
python pc/main.py
```

### 🎮 In-Game Controls:
- **Steer Left / Right**: Tilt ESP32 / `A` & `D` / Arrow Keys / Move Mouse
- **Turbo Boost**: Button 1 (GPIO 18) / `W` / `Up Arrow` / `Spacebar`
- **Brake / Decelerate**: Button 2 (GPIO 19) / `S` / `Down Arrow`
- **Cycle Themes (Press 'T')**: Countryside -> Sunset -> Night -> Rain -> City
- **Toggle CRT Scanlines**: Press **`C`**
- **Toggle Camera POV**: Press **`V`** (Driver's Cockpit <-> Chase)
- **Open Calibration GUI**: Press **`K`**
- **Zero-Center Steering**: Press **`R`** / `Spacebar` (in Calibration)
- **Pause Game**: Press **`P`**
- **Quit**: `ESC`
