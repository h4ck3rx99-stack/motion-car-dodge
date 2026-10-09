"""
=============================================================================
🎮 1990s 2D Arcade Racing Cabinet Game Loop
=============================================================================
Glues together 2D raster road projection, sprite-based traffic, roadside
scenery, driver cockpit POV, theme cycling, and ESP32 motion steering.
"""

import pygame

from camera import CameraManager
from config import (
    ARCADE_HEIGHT,
    ARCADE_WIDTH,
    FPS,
    STEER_DEADZONE_DEG,
    STEER_MAX_ANGLE_DEG,
    THEME_NAMES,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from controller import ControllerManager
from hud import HUDManager
from road import Highway
from sound_gen import SoundEngine
from sprites import SpriteFactory
from vehicles import PlayerCar, VehicleManager


class GameState:
    PLAYING = 0
    PAUSED = 1
    GAME_OVER = 2
    CALIBRATING = 3


class Game:
    """The central 1990s arcade racing cabinet game instance."""

    def __init__(self, screen: pygame.Surface, controller: ControllerManager):
        self.screen = screen
        self.controller = controller
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.PLAYING

        # 1. Native 1990s Arcade Canvas Buffer (320x224)
        self.arcade_canvas = pygame.Surface((ARCADE_WIDTH, ARCADE_HEIGHT))

        # 2. Sprite Factory
        self.sprite_factory = SpriteFactory()

        # 3. Core Subsystems
        self.highway = Highway(self.sprite_factory)
        self.player = PlayerCar()
        self.vehicle_mgr = VehicleManager(self.highway, self.sprite_factory)
        self.camera_mgr = CameraManager(self.sprite_factory)
        self.sound_engine = SoundEngine()
        self.hud = HUDManager()

        # Active Theme (0: Countryside, 1: Sunset, 2: Night, 3: Rainy, 4: City Outskirts)
        self.theme = 0
        self.enable_crt = True

        # Telemetry Cache
        self.last_steer_input = 0.0
        self.last_nitro = False
        self.last_brake = False
        self.last_cal_deg = 0.0
        self.last_raw_deg = 0.0

        # Start Procedural Audio
        self.sound_engine.start_engine_loop()
        self.time_sec = 0.0

    def restart(self):
        self.player = PlayerCar()
        self.vehicle_mgr = VehicleManager(self.highway, self.sprite_factory)
        self.state = GameState.PLAYING
        self.sound_engine.play("pickup", 0.7)

    def next_theme(self):
        self.theme = (self.theme + 1) % len(THEME_NAMES)
        self.sound_engine.play("click", 0.6)

    def toggle_crt(self):
        self.enable_crt = not self.enable_crt
        self.sound_engine.play("click", 0.5)

    def toggle_calibration(self):
        if self.state == GameState.CALIBRATING:
            self.state = GameState.PLAYING
        else:
            self.state = GameState.CALIBRATING
        self.sound_engine.play("click", 0.6)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.CALIBRATING:
                    self.state = GameState.PLAYING
                else:
                    self.running = False

            # 'V' Keybind to switch Camera POV (Cockpit <-> Chase)
            elif event.key == pygame.K_v:
                self.camera_mgr.toggle_mode()
                self.sound_engine.play("click", 0.6)

            # 'T' Keybind to cycle Themes
            elif event.key == pygame.K_t:
                self.next_theme()

            # 'C' Keybind to toggle CRT Scanlines
            elif event.key == pygame.K_c:
                self.toggle_crt()

            # 'K' Keybind to open Calibration Screen
            elif event.key == pygame.K_k:
                self.toggle_calibration()

            # 'R' Keybind to zero steering / restart
            elif event.key == pygame.K_r:
                if self.state == GameState.GAME_OVER:
                    self.restart()
                else:
                    self.controller.calibrate_center()
                    self.sound_engine.play("click", 0.6)

            elif event.key == pygame.K_p:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
                elif self.state == GameState.PAUSED:
                    self.state = GameState.PLAYING

            elif event.key == pygame.K_SPACE:
                if self.state == GameState.GAME_OVER:
                    self.restart()
                elif self.state == GameState.CALIBRATING:
                    self.controller.calibrate_center()
                    self.sound_engine.play("click", 0.6)

    def update(self, dt: float):
        self.time_sec += dt

        # 1. Read Keyboard Fallback Inputs
        keys = pygame.key.get_pressed()
        kb_steer = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            kb_steer -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            kb_steer += 1.0

        kb_nitro = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        kb_brake = keys[pygame.K_DOWN] or keys[pygame.K_s]

        self.controller.update_fallback_inputs(kb_steer, kb_nitro, kb_brake, False)

        # 2. Retrieve Frame Inputs from Hardware / Controller Bridge
        (
            steer_input,
            nitro_active,
            brake_active,
            pov_toggle_event,
            recal_event,
            cal_angle_deg,
            raw_angle_deg,
        ) = self.controller.get_frame_input()

        self.last_steer_input = steer_input
        self.last_nitro = nitro_active
        self.last_brake = brake_active
        self.last_cal_deg = cal_angle_deg
        self.last_raw_deg = raw_angle_deg

        if pov_toggle_event:
            self.camera_mgr.toggle_mode()
            self.sound_engine.play("click", 0.6)

        if self.state == GameState.CALIBRATING:
            return

        if self.player.lives <= 0:
            self.state = GameState.GAME_OVER
            if recal_event:
                self.restart()
            return

        # 3. Update Player Physics
        self.player.update(dt, steer_input, nitro_active, brake_active, self.highway.track_length)

        # 4. Update Traffic & Interactions
        self.vehicle_mgr.update(dt, self.player, self.highway.track_length, self.sound_engine)

        # 5. Update Camera
        self.camera_mgr.update_camera_pos(self.player, self.highway, dt)

        # 6. Audio Engine Pitch
        speed_ratio = self.player.speed / 160.0
        self.sound_engine.update_engine_pitch(speed_ratio, self.player.is_nitro_active)

    def render(self, dt: float):
        """Renders 100% 2D pixel-art arcade canvas (320x224) and scales up to display."""
        # 1. Total Frame Clear on 2D Arcade Canvas
        self.arcade_canvas.fill((0, 0, 0))

        # 2. Parallax Banded Arcade Sky & Layered Mountains
        self.highway.render_backdrop(self.arcade_canvas, self.camera_mgr.cam_x, self.time_sec, self.theme)

        # 3. 2D Raster Road & Scaled Roadside Scenery (Trees, Rocks, Poles, Diners)
        self.highway.render_road(
            self.arcade_canvas,
            self.camera_mgr.cam_x,
            self.camera_mgr.cam_y,
            self.camera_mgr.cam_z,
            self.theme
        )

        # 4. 2D Sprite-Scaled Traffic Vehicles & Pickups
        self.vehicle_mgr.render_traffic_and_items(
            self.arcade_canvas,
            self.camera_mgr.cam_x,
            self.camera_mgr.cam_y,
            self.camera_mgr.cam_z,
            self.highway.track_length
        )

        # 5. Driver's POV Interior Cockpit (Windshield frame, dashboard, animated wheel)
        self.camera_mgr.render_player_view(
            self.arcade_canvas,
            self.player,
            self.last_cal_deg,
            dt
        )

        # 6. 1990s Arcade HUD (SPEED, SCORE, GEAR, FUEL, LIVES)
        self.hud.render_hud(
            self.arcade_canvas,
            self.player,
            self.controller.connection_info,
            self.controller.is_connected,
            self.camera_mgr.mode,
            self.theme,
            self.last_cal_deg
        )

        # 7. Optional Arcade CRT Scanline Filter
        if self.enable_crt:
            self.hud.apply_crt_scanlines(self.arcade_canvas)

        # 8. Game Over Overlay
        if self.state == GameState.GAME_OVER:
            self.hud.render_game_over(self.arcade_canvas, self.player)

        # 9. Calibration Screen Overlay
        if self.state == GameState.CALIBRATING:
            self.hud.render_calibration_screen(
                self.arcade_canvas,
                self.controller.connection_info,
                self.controller.is_connected,
                self.last_raw_deg,
                self.last_cal_deg,
                self.last_steer_input,
                self.controller.center_offset_deg,
                STEER_DEADZONE_DEG,
                STEER_MAX_ANGLE_DEG
            )

        # 10. Pixel-Perfect Nearest-Neighbor Scaling to Screen
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        scaled_view = pygame.transform.scale(self.arcade_canvas, (sw, sh))
        self.screen.blit(scaled_view, (0, 0))

        pygame.display.flip()

    def run(self):
        """Main 60 FPS loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            if dt > 0.1:
                dt = 0.1

            for event in pygame.event.get():
                self.handle_event(event)

            if self.state != GameState.PAUSED and self.state != GameState.CALIBRATING:
                self.update(dt)
            elif self.state == GameState.CALIBRATING:
                self.update(0.0)

            self.render(dt)

        self.controller.shutdown()
        pygame.quit()
