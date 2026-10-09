"""
=============================================================================
🖥️ 1990s Arcade Cabinet HUD, Gauges & CRT Scanline Filter
=============================================================================
Chunky arcade font typography: SPEED, SCORE, GEAR, FUEL, DISTANCE,
and optional arcade CRT monitor scanlines.
"""

import math
import pygame

from config import (
    ARCADE_HEIGHT,
    ARCADE_WIDTH,
    THEME_NAMES,
)
from vehicles import PlayerCar


class HUDManager:
    """Manages 1990s arcade HUD overlays, gauges, and CRT scanlines."""

    def __init__(self):
        pygame.font.init()
        self.font_score = pygame.font.SysFont("impact", 13)
        self.font_speed = pygame.font.SysFont("impact", 18)
        self.font_gear = pygame.font.SysFont("impact", 12)
        self.font_title = pygame.font.SysFont("impact", 20)
        self.font_small = pygame.font.SysFont("consolas", 9, bold=True)

        # Pre-build CRT Scanline Overlay surface
        self.crt_scanlines = pygame.Surface((ARCADE_WIDTH, ARCADE_HEIGHT), pygame.SRCALPHA)
        for y in range(0, ARCADE_HEIGHT, 2):
            pygame.draw.line(self.crt_scanlines, (0, 0, 0, 45), (0, y), (ARCADE_WIDTH, y), 1)

    def render_hud(
        self,
        surface: pygame.Surface,
        player: PlayerCar,
        controller_info: str,
        is_connected: bool,
        camera_mode: str,
        theme: int,
        calibrated_angle_deg: float
    ):
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT

        # ---------------------------------------------------------------------
        # 1. TOP ARCADE BANNER: Score, Distance, Speed, Lives
        # ---------------------------------------------------------------------
        # Score (Top Left)
        sc_lbl = self.font_small.render("SCORE", False, (255, 220, 0))
        sc_val = self.font_score.render(f"{player.score:06d}", False, (255, 255, 255))
        surface.blit(sc_lbl, (8, 2))
        surface.blit(sc_val, (8, 12))

        # Speed (Top Center-Left)
        spd_kmh = int(player.speed)
        sp_lbl = self.font_small.render("SPEED", False, (0, 220, 255))
        sp_val = self.font_speed.render(f"{spd_kmh}", False, (255, 255, 255) if not player.is_nitro_active else (255, 60, 140))
        sp_unit = self.font_small.render("MPH", False, (0, 220, 255))
        surface.blit(sp_lbl, (110, 2))
        surface.blit(sp_val, (108, 11))
        surface.blit(sp_unit, (140, 16))

        # Gear (LO / HI)
        gear_name = "HI" if player.speed > 85.0 else "LO"
        g_lbl = self.font_small.render("GEAR", False, (255, 180, 0))
        g_val = self.font_score.render(gear_name, False, (255, 255, 255))
        surface.blit(g_lbl, (180, 2))
        surface.blit(g_val, (182, 12))

        # Lives (Top Right)
        l_lbl = self.font_small.render("LIVES", False, (255, 40, 70))
        surface.blit(l_lbl, (245, 2))
        for i in range(3):
            lx = 245 + i * 14
            ly = 18
            col = (255, 40, 70) if i < player.lives else (50, 55, 65)
            pygame.draw.rect(surface, col, (lx, ly, 10, 8), border_radius=2)

        # ---------------------------------------------------------------------
        # 2. BOTTOM CORNER METERS: Fuel & Nitro
        # ---------------------------------------------------------------------
        # Fuel Meter (Bottom Left)
        f_lbl = self.font_small.render("FUEL", False, (255, 255, 255))
        surface.blit(f_lbl, (8, sh - 18))
        pygame.draw.rect(surface, (30, 35, 45), (34, sh - 16, 50, 8))
        fill_f = int(50 * (player.fuel / 100.0))
        f_col = (255, 40, 40) if player.fuel < 25.0 else (40, 220, 80)
        if fill_f > 0:
            pygame.draw.rect(surface, f_col, (34, sh - 16, fill_f, 8))
        pygame.draw.rect(surface, (200, 210, 230), (34, sh - 16, 50, 8), 1)

        # Nitro Meter (Bottom Right)
        n_lbl = self.font_small.render("TURBO", False, (0, 220, 255))
        surface.blit(n_lbl, (sw - 88, sh - 18))
        pygame.draw.rect(surface, (30, 35, 45), (sw - 54, sh - 16, 46, 8))
        fill_n = int(46 * (player.nitro_charge / 100.0))
        n_col = (0, 240, 255) if not player.is_nitro_active else (255, 30, 120)
        if fill_n > 0:
            pygame.draw.rect(surface, n_col, (sw - 54, sh - 16, fill_n, 8))
        pygame.draw.rect(surface, (200, 210, 230), (sw - 54, sh - 16, 46, 8), 1)

        # ---------------------------------------------------------------------
        # 3. NOTIFICATION BANNERS (Close Call, Fuel Collected, Low Fuel)
        # ---------------------------------------------------------------------
        if player.fuel_alert_timer > 0:
            f_txt = self.font_title.render("+FUEL RESTORED!", False, (0, 255, 128))
            surface.blit(f_txt, (sw // 2 - f_txt.get_width() // 2, 28))

        elif player.near_miss_combo > 0:
            combo_txt = f"CLOSE CALL! {player.near_miss_combo}x"
            c_surf = self.font_title.render(combo_txt, False, (255, 40, 120))
            surface.blit(c_surf, (sw // 2 - c_surf.get_width() // 2, 28))

        # Low Fuel Warning Flash
        if player.fuel < 25 and int(player.distance_miles * 80) % 2 == 0:
            w_surf = self.font_title.render("! GET FUEL ON ROAD !", False, (255, 35, 35))
            surface.blit(w_surf, (sw // 2 - w_surf.get_width() // 2, 48))

    def apply_crt_scanlines(self, surface: pygame.Surface):
        """Blits subtle CRT monitor scanline texture."""
        surface.blit(self.crt_scanlines, (0, 0))

    def render_game_over(self, surface: pygame.Surface, player: PlayerCar):
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 235))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("GAME OVER", False, (255, 40, 60))
        surface.blit(title, (sw // 2 - title.get_width() // 2, 45))

        sc_txt = self.font_score.render(f"FINAL SCORE: {player.score:06d}", False, (255, 255, 255))
        dist_txt = self.font_score.render(f"DISTANCE: {player.distance_miles:.2f} MILES", False, (255, 220, 0))
        top_txt = self.font_score.render(f"TOP SPEED: {int(player.top_speed)} MPH", False, (0, 220, 255))
        surface.blit(sc_txt, (sw // 2 - sc_txt.get_width() // 2, 85))
        surface.blit(dist_txt, (sw // 2 - dist_txt.get_width() // 2, 105))
        surface.blit(top_txt, (sw // 2 - top_txt.get_width() // 2, 125))

        rst = self.font_small.render("PRESS SPACE / BUTTON TO RESTART", False, (200, 220, 250))
        surface.blit(rst, (sw // 2 - rst.get_width() // 2, 160))

    def render_calibration_screen(
        self,
        surface: pygame.Surface,
        controller_info: str,
        is_connected: bool,
        raw_angle_deg: float,
        calibrated_angle_deg: float,
        steer_axis: float,
        center_offset_deg: float,
        deadzone_deg: float,
        max_angle_deg: float
    ):
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 245))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("STEERING CALIBRATION", False, (0, 230, 255))
        surface.blit(title, (sw // 2 - title.get_width() // 2, 12))

        stat_col = (0, 255, 128) if is_connected else (255, 160, 40)
        stat_txt = self.font_small.render(f"DEVICE: {controller_info}", False, stat_col)
        surface.blit(stat_txt, (sw // 2 - stat_txt.get_width() // 2, 40))

        # Digital Spirit Level Tilt Bar
        gw = 220
        gh = 22
        gx = sw // 2 - gw // 2
        gy = 60
        pygame.draw.rect(surface, (15, 20, 30), (gx, gy, gw, gh), border_radius=4)
        pygame.draw.rect(surface, (60, 75, 100), (gx, gy, gw, gh), 1, border_radius=4)

        # Center line & deadzone
        dz_px = int((deadzone_deg / max_angle_deg) * (gw // 2))
        pygame.draw.rect(surface, (0, 255, 128, 60), (sw // 2 - dz_px, gy + 1, dz_px * 2, gh - 2))
        pygame.draw.line(surface, (0, 255, 128), (sw // 2, gy), (sw // 2, gy + gh), 1)

        # Bubble
        clamped_deg = max(-max_angle_deg, min(max_angle_deg, calibrated_angle_deg))
        bx = sw // 2 + int((clamped_deg / max_angle_deg) * (gw // 2 - 12))
        b_col = (0, 255, 128) if abs(calibrated_angle_deg) <= deadzone_deg else (255, 220, 0)
        pygame.draw.circle(surface, b_col, (bx, gy + gh // 2), 7)
        pygame.draw.circle(surface, (255, 255, 255), (bx, gy + gh // 2), 7, 1)

        # Readouts
        d1 = self.font_small.render(f"ANGLE: {calibrated_angle_deg:+.1f} DEG", False, (255, 255, 255))
        d2 = self.font_small.render(f"STEER: {int(steer_axis * 100):+d}%", False, (0, 220, 255))
        d3 = self.font_small.render(f"OFFSET: {center_offset_deg:+.1f} DEG", False, (255, 220, 0))
        surface.blit(d1, (50, 95))
        surface.blit(d2, (180, 95))
        surface.blit(d3, (50, 115))

        # Instructions
        inst1 = self.font_small.render("HOLD WHEEL LEVEL -> PRESS SPACE TO ZERO", False, (255, 230, 0))
        inst2 = self.font_small.render("PRESS [K] OR [ESC] TO RETURN TO GAME", False, (0, 220, 255))
        surface.blit(inst1, (sw // 2 - inst1.get_width() // 2, 145))
        surface.blit(inst2, (sw // 2 - inst2.get_width() // 2, 165))
