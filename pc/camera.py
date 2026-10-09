"""
=============================================================================
🎥 Driver's POV Interior Cockpit & Windshield Rendering Engine
=============================================================================
Renders authentic 1990s arcade driver's interior: Windshield frame,
chunky dark dashboard, analog speedometer needle, gear display, and an
animated pixel steering wheel that rotates with real-time ESP32 tilt.
"""

import math
import pygame

from config import (
    ARCADE_HEIGHT,
    ARCADE_WIDTH,
    CAMERA_MODE_EXTERIOR,
    CAMERA_MODE_INTERIOR,
    EXTERIOR_CAM_HEIGHT,
    INTERIOR_CAM_HEIGHT,
    ROAD_WIDTH,
)
from vehicles import PlayerCar


class CameraManager:
    """Manages the Driver's POV Cockpit and camera tracking."""

    def __init__(self, sprite_factory):
        self.factory = sprite_factory
        self.mode = CAMERA_MODE_INTERIOR  # Default: Driver's POV inside car
        self.cam_x = 0.0
        self.cam_y = INTERIOR_CAM_HEIGHT
        self.cam_z = 0.0
        self.wheel_angle_rad = 0.0

    def toggle_mode(self) -> str:
        self.mode = CAMERA_MODE_EXTERIOR if self.mode == CAMERA_MODE_INTERIOR else CAMERA_MODE_INTERIOR
        return self.mode

    def update_camera_pos(self, player: PlayerCar, highway_track, dt: float):
        # Camera X follows player lane position
        target_x = player.x * (ROAD_WIDTH * 0.38)
        self.cam_z = player.z
        self.cam_x += (target_x - self.cam_x) * 12.0 * dt

        player_seg = highway_track.find_segment(player.z)
        target_y = player_seg.p1_world.y + (
            INTERIOR_CAM_HEIGHT if self.mode == CAMERA_MODE_INTERIOR else EXTERIOR_CAM_HEIGHT
        )
        self.cam_y += (target_y - self.cam_y) * 12.0 * dt

        # Smooth steering wheel rotation
        target_wheel = player.steering_angle * 1.35
        self.wheel_angle_rad += (target_wheel - self.wheel_angle_rad) * 20.0 * dt

    def render_player_view(
        self,
        surface: pygame.Surface,
        player: PlayerCar,
        calibrated_angle_deg: float,
        dt: float
    ):
        if self.mode == CAMERA_MODE_INTERIOR:
            self._render_driver_cockpit(surface, player, calibrated_angle_deg)
        else:
            self._render_exterior_sprite(surface, player)

    # -------------------------------------------------------------------------
    # DRIVER'S POV COCKPIT (Primary 1990s Arcade View)
    # -------------------------------------------------------------------------
    def _render_driver_cockpit(
        self,
        surface: pygame.Surface,
        player: PlayerCar,
        calibrated_angle_deg: float
    ):
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT

        # 1. Slender Windshield A-Pillars & Top Header Frame
        # Left A-Pillar
        pygame.draw.polygon(surface, (18, 20, 26), [(0, 0), (14, 0), (8, sh), (0, sh)])
        # Right A-Pillar
        pygame.draw.polygon(surface, (18, 20, 26), [(sw - 14, 0), (sw, 0), (sw, sh), (sw - 8, sh)])
        # Top Roof Header
        pygame.draw.rect(surface, (14, 16, 22), (0, 0, sw, 6))

        # 2. Wide Rear-View Mirror (Top Center)
        mw = 64
        mh = 14
        mx = sw // 2 - mw // 2
        my = 2
        pygame.draw.rect(surface, (24, 26, 34), (mx - 2, my - 2, mw + 4, mh + 4), border_radius=2)
        pygame.draw.rect(surface, (15, 28, 45), (mx, my, mw, mh), border_radius=2)
        pygame.draw.rect(surface, (60, 80, 110), (mx, my, mw, mh), 1, border_radius=2)
        # Mirror Horizon line
        pygame.draw.line(surface, (35, 60, 95), (mx + 2, my + mh // 2), (mx + mw - 2, my + mh // 2), 1)

        # 3. Lower Molded Dashboard (Bottom 44 pixels: Y=180 to Y=224)
        dash_sprite = self.factory.sprites["cockpit_dash"]
        dash_y = sh - dash_sprite.get_height()
        surface.blit(dash_sprite, (0, dash_y))

        # 4. Animated Rotating Steering Wheel (Driver's side: X ~ 95, Y ~ 195)
        base_wheel = self.factory.sprites["steering_wheel"]
        rot_wheel = pygame.transform.rotate(base_wheel, -math.degrees(self.wheel_angle_rad))

        wx = int(sw * 0.30)
        wy = int(sh * 0.90)
        surface.blit(rot_wheel, (wx - rot_wheel.get_width() // 2, wy - rot_wheel.get_height() // 2))

        # 5. Analog Speedometer Needle (Inside instrument binnacle behind wheel)
        gx = wx
        gy = wy - 26
        speed_ratio = min(1.0, player.speed / 220.0)
        needle_angle = 2.4 - speed_ratio * 3.1
        nx = gx + math.cos(needle_angle) * 8
        ny = gy - math.sin(needle_angle) * 8
        pygame.draw.circle(surface, (10, 14, 20), (gx, gy), 10)
        pygame.draw.circle(surface, (0, 210, 255), (gx, gy), 10, 1)
        pygame.draw.line(surface, (255, 40, 40), (gx, gy), (int(nx), int(ny)), 2)
        pygame.draw.circle(surface, (255, 255, 255), (gx, gy), 2)

        # 6. Center Console Digital Display (Gear)
        cx = 144
        cy = dash_y + 28
        gear_txt = "HI" if player.speed > 85.0 else "LO"
        font = pygame.font.SysFont("impact", 9)
        g_surf = font.render(gear_txt, False, (255, 220, 0))
        surface.blit(g_surf, (cx + 4, cy + 1))

    # -------------------------------------------------------------------------
    # 3RD-PERSON EXTERIOR SPRITE
    # -------------------------------------------------------------------------
    def _render_exterior_sprite(self, surface: pygame.Surface, player: PlayerCar):
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT

        cx = sw // 2 + int(player.x * (sw * 0.24))
        cy = int(sh * 0.88)

        base_sprite = self.factory.sprites["car_sports"]
        bw, bh = base_sprite.get_size()
        scaled_w = int(bw * 1.5)
        scaled_h = int(bh * 1.5)

        # Ground Shadow
        pygame.draw.ellipse(surface, (12, 14, 18), (cx - scaled_w // 2 - 4, cy - 4, scaled_w + 8, 8))

        scaled_sprite = pygame.transform.scale(base_sprite, (scaled_w, scaled_h))
        surface.blit(scaled_sprite, (cx - scaled_w // 2, cy - scaled_h))

        # Nitro Exhaust Flames
        if player.is_nitro_active:
            pygame.draw.rect(surface, (0, 240, 255), (cx - 8, cy - 2, 3, 6))
            pygame.draw.rect(surface, (0, 240, 255), (cx + 5, cy - 2, 3, 6))
