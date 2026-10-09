"""
=============================================================================
⚙️ 1990s 2D Arcade Racing Cabinet - Configuration & Constants
=============================================================================
Deliberate 2D sprite-based pseudo-3D raster rendering, chunky pixel art,
discrete color palettes, cockpit driver POV, and 1990s arcade aesthetics.
"""

import os

# ---------------------------------------------------------------------------
# Native 1990s Arcade Resolution & Fullscreen Scaling
# ---------------------------------------------------------------------------
ARCADE_WIDTH = 320
ARCADE_HEIGHT = 224
HORIZON_Y = 92                # Vanishing point horizon line

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FULLSCREEN = True
FPS = 60
TITLE = "🏁 OUTDRIVE 1992 - 90s Arcade Driver POV"

# ---------------------------------------------------------------------------
# Themes & Environments
# ---------------------------------------------------------------------------
THEME_COUNTRYSIDE = 0   # Sunny green pastures, pine trees, farmhouses, blue sky
THEME_SUNSET = 1        # Warm golden/magenta sunset, glowing sun, mountain silhouettes
THEME_NIGHT = 2         # Indigo night highway, glowing streetlights, distant city skyline
THEME_RAINY = 3         # Slate overcast sky, rain streaks, wet reflective asphalt
THEME_CITY_OUTSKIRTS = 4# Industrial warehouses, billboards, gas stations, factory smoke

THEME_NAMES = [
    "SUNNY COUNTRYSIDE",
    "SUNSET HIGHWAY",
    "NIGHT RUNNER",
    "STORM DRIFT",
    "CITY OUTSKIRTS"
]

# ---------------------------------------------------------------------------
# Camera POV Modes & Heights
# ---------------------------------------------------------------------------
CAMERA_MODE_INTERIOR = "FIRST_PERSON"
CAMERA_MODE_EXTERIOR = "THIRD_PERSON"

INTERIOR_CAM_HEIGHT = 280.0   # Driver's eye level
EXTERIOR_CAM_HEIGHT = 380.0   # Chase cam level

# ---------------------------------------------------------------------------
# Serial & Hardware Controller Settings
# ---------------------------------------------------------------------------
SERIAL_BAUD = 115200
DEFAULT_COM_PORT = None

STEER_MAX_ANGLE_DEG = 22.0    # Degrees tilt for full steer lock
STEER_DEADZONE_DEG = 1.2      # Tiny deadzone to eliminate sensor jitter
STEER_SMOOTHING = 0.08        # Instantaneous arcade response
STEER_SENSITIVITY = 1.8       # Fast arcade lane switching
INVERT_STEERING = False
GYRO_RATE_SENSITIVITY = 0.045

# ---------------------------------------------------------------------------
# Road & 2D Raster Geometry (Increased Render Distance)
# ---------------------------------------------------------------------------
ROAD_WIDTH = 1600.0           # World road width
SEGMENT_LENGTH = 180.0        # Length per road segment
DRAW_DISTANCE = 220           # Increased visible segments ahead
CAMERA_DEPTH = 0.84           # Perspective field of view
LANES_COUNT = 4               # 4-lane highway (Left 2 Oncoming, Right 2 Forward)

# ---------------------------------------------------------------------------
# Vehicle Speeds & Arcade Physics (Balanced & Reduced Speed)
# ---------------------------------------------------------------------------
BASE_MIN_SPEED = 45.0         # Comfortable cruise speed (MPH)
BASE_MAX_SPEED = 115.0        # Top cruise speed (MPH)
NITRO_MAX_SPEED = 160.0       # Turbo speed (MPH)
ACCEL_RATE = 45.0             # Smooth acceleration
BRAKE_RATE = 90.0             # Responsive braking
LATERAL_SPEED = 5.5           # Agile lateral lane shifting
MAX_ROAD_BOUND = 1.25

# ---------------------------------------------------------------------------
# Fuel & Turbo Mechanics
# ---------------------------------------------------------------------------
MAX_FUEL = 100.0
FUEL_BURN_RATE = 3.2          # Percent per second
FUEL_PICKUP_AMOUNT = 35.0
NITRO_MAX_CHARGE = 100.0
NITRO_DRAIN_RATE = 24.0
NITRO_RECHARGE_RATE = 8.5
MAX_PLAYER_LIVES = 3
SHIELD_DURATION_SEC = 8.0
