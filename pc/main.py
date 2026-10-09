"""
=============================================================================
🏁 OUTDRIVE 1992 - 1990s 2D Arcade Driver POV Highway Racer
=============================================================================
Launch with:
    python pc/main.py
"""

import ctypes
import os
import sys

# Ensure local directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from config import FULLSCREEN, TITLE, WINDOW_HEIGHT, WINDOW_WIDTH
from controller import ControllerManager
from game import Game


def setup_windows_dpi():
    """Enable crisp pixel scaling on high-DPI Windows displays."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def main():
    setup_windows_dpi()
    pygame.init()
    pygame.mixer.init()

    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.display.set_caption(TITLE)

    # Launch in true Fullscreen matching native desktop display resolution
    if FULLSCREEN:
        info = pygame.display.Info()
        screen_w = info.current_w if info.current_w > 0 else WINDOW_WIDTH
        screen_h = info.current_h if info.current_h > 0 else WINDOW_HEIGHT
        screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
    else:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)

    controller = ControllerManager()
    game = Game(screen, controller)

    print("=========================================================")
    print("🏁  OUTDRIVE 1992 - 1990s 2D Arcade Driver's POV Racer")
    print("=========================================================")
    print("🎮 Controls:")
    print("   • ESP32 Tilt: Physical Motion Steering")
    print("   • Keyboard Steering: 'A' / 'D' or Left / Right Arrows")
    print("   • Turbo Boost: Button 1 (GPIO 18) / 'W' / Up Arrow / Spacebar")
    print("   • Brake: Button 2 (GPIO 19) / 'S' / Down Arrow")
    print("   • 'T' Key: Cycle Themes (Countryside, Sunset, Night, Rainy, City)")
    print("   • 'C' Key: Toggle 1990s CRT Monitor Scanlines")
    print("   • 'V' Key: Toggle POV (Driver's Cockpit <-> Chase)")
    print("   • 'K' Key: Open Gyro Spirit Level Calibration GUI")
    print("   • 'R' Key: Zero-Center Steering Calibration / Restart")
    print("   • 'P' Key: Pause Game")
    print("   • ESC: Quit")
    print("=========================================================")

    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        controller.shutdown()
        pygame.quit()


if __name__ == "__main__":
    main()
