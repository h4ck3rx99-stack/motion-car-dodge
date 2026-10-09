"""
=============================================================================
🎨 1990s Arcade 2D Pixel-Art Sprite Factory
=============================================================================
Generates authentic 2D pixel-art sprites for:
  - Traffic vehicles (Sports cars, Sedans, 18-wheeler trucks, Vans, Buses, Bikes)
  - Roadside environment (Pine trees, Oaks, Boulders, Poles, Diners, Gas stations)
  - Fuel cans & powerups (High-contrast red Jerry Cans, Gold coins, Nitro, Shields)
  - Driver's interior cockpit (Windshield frame, dashboard, animated steering wheel)
"""

import math
import pygame


class SpriteFactory:
    """Pre-renders and caches authentic 1990s arcade 2D pixel-art sprite assets."""

    def __init__(self):
        self.sprites = {}
        self._build_all_sprites()

    def _build_all_sprites(self):
        # 1. Traffic Vehicles (Chunky, high-contrast 1990s arcade sprites)
        self.sprites["car_sports"] = self._create_sports_car()
        self.sprites["car_sedan"] = self._create_sedan()
        self.sprites["car_truck"] = self._create_semi_truck()
        self.sprites["car_van"] = self._create_van()
        self.sprites["car_bus"] = self._create_bus()
        self.sprites["car_bike"] = self._create_motorcycle()

        # 2. Scenery & Roadside Props
        self.sprites["pine_tree"] = self._create_pine_tree()
        self.sprites["oak_tree"] = self._create_oak_tree()
        self.sprites["palm_tree"] = self._create_palm_tree()
        self.sprites["rock_boulder"] = self._create_rock_boulder()
        self.sprites["telephone_pole"] = self._create_telephone_pole()
        self.sprites["billboard_1"] = self._create_billboard("OUTDRIVE", (230, 40, 60), (255, 220, 0))
        self.sprites["billboard_2"] = self._create_billboard("TURBO OIL", (30, 100, 220), (240, 240, 250))
        self.sprites["billboard_3"] = self._create_billboard("SYNTH COLA", (180, 20, 140), (0, 240, 255))
        self.sprites["gas_station"] = self._create_gas_station()
        self.sprites["diner"] = self._create_diner()
        self.sprites["warehouse"] = self._create_warehouse()
        self.sprites["farmhouse"] = self._create_farmhouse()
        self.sprites["barrel"] = self._create_construction_barrel()

        # 3. Collectibles (Bright & High-Contrast)
        self.sprites["item_fuel"] = self._create_fuel_can()
        self.sprites["item_coin"] = self._create_coin()
        self.sprites["item_nitro"] = self._create_nitro_bottle()
        self.sprites["item_shield"] = self._create_shield_orb()

        # 4. Interior Cockpit Dashboard
        self.sprites["cockpit_dash"] = self._create_cockpit_dashboard()
        self.sprites["steering_wheel"] = self._create_pixel_steering_wheel()

    # -------------------------------------------------------------------------
    # 2D PIXEL VEHICLES (Chunky 90s Arcade Sprites)
    # -------------------------------------------------------------------------
    def _create_sports_car(self) -> pygame.Surface:
        """Red Supercar (36x22 pixel sprite)."""
        s = pygame.Surface((36, 22), pygame.SRCALPHA)
        s.fill((16, 16, 20), (2, 11, 6, 11))
        s.fill((16, 16, 20), (28, 11, 6, 11))
        s.fill((180, 185, 200), (4, 13, 2, 7))
        s.fill((180, 185, 200), (30, 13, 2, 7))
        s.fill((235, 30, 40), (5, 7, 26, 13))
        s.fill((170, 15, 25), (5, 15, 26, 5))
        s.fill((25, 35, 55), (9, 2, 18, 7))
        s.fill((70, 120, 200), (10, 3, 16, 3))
        s.fill((255, 220, 30), (3, 4, 30, 2))
        s.fill((255, 20, 30), (6, 13, 6, 4))
        s.fill((255, 20, 30), (24, 13, 6, 4))
        s.fill((255, 240, 80), (14, 14, 8, 3))
        s.fill((200, 205, 220), (10, 18, 3, 2))
        s.fill((200, 205, 220), (23, 18, 3, 2))
        return s

    def _create_sedan(self) -> pygame.Surface:
        """Yellow City Sedan / Taxi (34x22 pixel sprite)."""
        s = pygame.Surface((34, 22), pygame.SRCALPHA)
        s.fill((16, 16, 20), (2, 11, 5, 11))
        s.fill((16, 16, 20), (27, 11, 5, 11))
        s.fill((245, 195, 25), (4, 7, 26, 13))
        s.fill((185, 140, 15), (4, 15, 26, 5))
        for x in range(6, 28, 4):
            s.fill((20, 20, 25), (x, 11, 2, 2))
        s.fill((35, 55, 85), (8, 2, 18, 7))
        s.fill((110, 160, 230), (9, 3, 16, 3))
        s.fill((255, 255, 255), (13, 0, 8, 3))
        s.fill((255, 20, 30), (5, 13, 5, 4))
        s.fill((255, 20, 30), (24, 13, 5, 4))
        return s

    def _create_semi_truck(self) -> pygame.Surface:
        """Heavy 18-Wheeler Cargo Rig (48x40 pixel sprite)."""
        s = pygame.Surface((48, 40), pygame.SRCALPHA)
        s.fill((35, 95, 210), (4, 4, 40, 26))
        s.fill((25, 70, 160), (4, 4, 40, 26), 2)
        for y in range(8, 28, 5):
            s.fill((190, 220, 255), (6, y, 36, 1))
        s.fill((45, 48, 55), (6, 30, 36, 8))
        s.fill((18, 18, 22), (2, 28, 6, 12))
        s.fill((18, 18, 22), (40, 28, 6, 12))
        s.fill((18, 18, 22), (9, 31, 5, 9))
        s.fill((18, 18, 22), (34, 31, 5, 9))
        s.fill((210, 220, 240), (1, 0, 3, 28))
        s.fill((210, 220, 240), (44, 0, 3, 28))
        for x in range(8, 40, 6):
            s.fill((255, 215, 20), (x, 33, 3, 3))
        s.fill((255, 20, 30), (6, 35, 5, 3))
        s.fill((255, 20, 30), (37, 35, 5, 3))
        return s

    def _create_van(self) -> pygame.Surface:
        """White Commercial Delivery Van (38x26 pixel sprite)."""
        s = pygame.Surface((38, 26), pygame.SRCALPHA)
        s.fill((16, 16, 20), (2, 14, 6, 12))
        s.fill((16, 16, 20), (30, 14, 6, 12))
        s.fill((245, 245, 252), (5, 4, 28, 20))
        s.fill((185, 190, 205), (5, 18, 28, 6))
        s.fill((55, 60, 70), (18, 5, 2, 18))
        s.fill((40, 65, 95), (8, 6, 8, 6))
        s.fill((40, 65, 95), (22, 6, 8, 6))
        s.fill((255, 20, 30), (6, 16, 3, 6))
        s.fill((255, 20, 30), (29, 16, 3, 6))
        return s

    def _create_bus(self) -> pygame.Surface:
        """Green Transit Highway Bus (44x34 pixel sprite)."""
        s = pygame.Surface((44, 34), pygame.SRCALPHA)
        s.fill((16, 16, 20), (2, 22, 6, 12))
        s.fill((16, 16, 20), (36, 22, 6, 12))
        s.fill((45, 150, 85), (4, 4, 36, 26))
        s.fill((30, 105, 60), (4, 22, 36, 8))
        s.fill((160, 210, 255), (7, 6, 30, 8))
        for x in range(12, 36, 6):
            s.fill((30, 75, 50), (x, 6, 1, 8))
        s.fill((255, 20, 30), (6, 26, 4, 4))
        s.fill((255, 20, 30), (34, 26, 4, 4))
        return s

    def _create_motorcycle(self) -> pygame.Surface:
        """Sports Motorcycle & Rider (18x26 pixel sprite)."""
        s = pygame.Surface((18, 26), pygame.SRCALPHA)
        s.fill((16, 16, 20), (7, 16, 4, 10))
        s.fill((235, 35, 45), (5, 11, 8, 7))
        s.fill((200, 205, 220), (11, 15, 3, 7))
        s.fill((255, 20, 30), (7, 12, 4, 2))
        s.fill((30, 35, 45), (5, 4, 8, 9))
        s.fill((255, 220, 30), (6, 1, 6, 5))
        s.fill((15, 15, 20), (7, 3, 4, 2))
        return s

    # -------------------------------------------------------------------------
    # 2D SCENERY & ROADSIDE OBJECTS
    # -------------------------------------------------------------------------
    def _create_pine_tree(self) -> pygame.Surface:
        s = pygame.Surface((32, 56), pygame.SRCALPHA)
        s.fill((90, 55, 30), (14, 42, 4, 14))
        tiers = [(16, 4, 12, 12), (16, 14, 20, 14), (16, 24, 26, 16), (16, 34, 30, 16)]
        for cx, top_y, w, h in tiers:
            pts = [(cx, top_y), (cx - w // 2, top_y + h), (cx + w // 2, top_y + h)]
            pygame.draw.polygon(s, (30, 115, 48), pts)
            pts_dark = [(cx, top_y), (cx - w // 2, top_y + h), (cx, top_y + h)]
            pygame.draw.polygon(s, (20, 85, 38), pts_dark)
        return s

    def _create_oak_tree(self) -> pygame.Surface:
        s = pygame.Surface((44, 52), pygame.SRCALPHA)
        s.fill((85, 50, 25), (19, 32, 6, 20))
        pygame.draw.circle(s, (35, 130, 48), (22, 20), 18)
        pygame.draw.circle(s, (48, 155, 60), (14, 22), 12)
        pygame.draw.circle(s, (52, 168, 65), (30, 22), 12)
        pygame.draw.circle(s, (25, 100, 38), (22, 10), 10)
        return s

    def _create_palm_tree(self) -> pygame.Surface:
        s = pygame.Surface((36, 60), pygame.SRCALPHA)
        for i in range(10):
            tx = 18 + int(math.sin(i * 0.3) * 4)
            ty = 56 - i * 4
            s.fill((125, 90, 48), (tx, ty, 5, 5))
        for angle in (0, 0.6, 1.3, 2.0, 2.6, 3.14):
            ex = int(20 + math.cos(angle) * 16)
            ey = int(18 - math.sin(angle) * 12)
            pygame.draw.line(s, (35, 150, 50), (20, 20), (ex, ey), 3)
        return s

    def _create_rock_boulder(self) -> pygame.Surface:
        s = pygame.Surface((32, 20), pygame.SRCALPHA)
        pts = [(0, 19), (6, 6), (16, 2), (26, 5), (31, 19)]
        pygame.draw.polygon(s, (135, 130, 125), pts)
        pts_shadow = [(0, 19), (6, 6), (16, 2), (14, 19)]
        pygame.draw.polygon(s, (90, 85, 80), pts_shadow)
        pygame.draw.lines(s, (50, 48, 45), True, pts, 1)
        return s

    def _create_telephone_pole(self) -> pygame.Surface:
        s = pygame.Surface((24, 64), pygame.SRCALPHA)
        s.fill((105, 75, 45), (10, 0, 4, 64))
        s.fill((105, 75, 45), (2, 8, 20, 3))
        s.fill((190, 200, 210), (3, 6, 2, 3))
        s.fill((190, 200, 210), (19, 6, 2, 3))
        pygame.draw.line(s, (75, 55, 35), (6, 11), (12, 16), 1)
        pygame.draw.line(s, (75, 55, 35), (18, 11), (12, 16), 1)
        return s

    def _create_billboard(self, text: str, bg_col, text_col) -> pygame.Surface:
        s = pygame.Surface((54, 40), pygame.SRCALPHA)
        s.fill((115, 120, 135), (12, 22, 3, 18))
        s.fill((115, 120, 135), (39, 22, 3, 18))
        s.fill((20, 22, 28), (0, 0, 54, 24))
        s.fill(bg_col, (2, 2, 50, 20))
        font = pygame.font.SysFont("impact", 9)
        txt_s = font.render(text, False, text_col)
        s.blit(txt_s, (27 - txt_s.get_width() // 2, 12 - txt_s.get_height() // 2))
        return s

    def _create_gas_station(self) -> pygame.Surface:
        s = pygame.Surface((64, 36), pygame.SRCALPHA)
        s.fill((215, 220, 230), (10, 12, 4, 24))
        s.fill((215, 220, 230), (50, 12, 4, 24))
        s.fill((230, 35, 45), (0, 0, 64, 12))
        s.fill((255, 255, 255), (0, 4, 64, 4))
        s.fill((245, 185, 25), (18, 22, 6, 14))
        s.fill((35, 110, 230), (40, 22, 6, 14))
        return s

    def _create_diner(self) -> pygame.Surface:
        s = pygame.Surface((56, 34), pygame.SRCALPHA)
        s.fill((205, 210, 220), (0, 10, 56, 24))
        s.fill((230, 40, 60), (0, 10, 56, 4))
        for x in range(6, 50, 10):
            s.fill((65, 115, 175), (x, 16, 7, 10))
        s.fill((255, 0, 128), (14, 2, 28, 8))
        return s

    def _create_warehouse(self) -> pygame.Surface:
        s = pygame.Surface((60, 36), pygame.SRCALPHA)
        s.fill((135, 140, 150), (0, 10, 60, 26))
        pygame.draw.polygon(s, (85, 90, 100), [(0, 10), (30, 0), (60, 10)])
        s.fill((55, 60, 70), (18, 16, 24, 20))
        for y in range(18, 36, 4):
            s.fill((95, 100, 110), (19, y, 22, 1))
        return s

    def _create_farmhouse(self) -> pygame.Surface:
        s = pygame.Surface((48, 34), pygame.SRCALPHA)
        s.fill((240, 240, 245), (4, 12, 40, 22))
        pygame.draw.polygon(s, (190, 45, 45), [(0, 12), (24, 0), (48, 12)])
        s.fill((55, 80, 115), (10, 16, 8, 8))
        s.fill((55, 80, 115), (30, 16, 8, 8))
        s.fill((105, 65, 35), (20, 22, 8, 12))
        return s

    def _create_construction_barrel(self) -> pygame.Surface:
        s = pygame.Surface((12, 18), pygame.SRCALPHA)
        s.fill((245, 95, 25), (1, 0, 10, 18))
        s.fill((255, 255, 255), (1, 4, 10, 3))
        s.fill((255, 255, 255), (1, 11, 10, 3))
        return s

    # -------------------------------------------------------------------------
    # COLLECTIBLES (Bright & High-Contrast 20x20 Jerry Can & Pickups)
    # -------------------------------------------------------------------------
    def _create_fuel_can(self) -> pygame.Surface:
        """Bright Red High-Contrast Jerry Can (22x22 pixels)."""
        s = pygame.Surface((22, 22), pygame.SRCALPHA)
        # Red Jerry Can Body
        s.fill((240, 30, 35), (2, 5, 18, 16))
        pygame.draw.rect(s, (15, 15, 20), (2, 5, 18, 16), 1)
        # Top Handle
        s.fill((255, 255, 255), (6, 1, 10, 4))
        pygame.draw.rect(s, (15, 15, 20), (6, 1, 10, 4), 1)
        # Yellow Fuel Spout
        s.fill((255, 220, 0), (16, 2, 4, 4))
        # Bold Yellow 'GAS' / 'F' Stamp
        s.fill((255, 235, 0), (6, 9, 10, 3))
        s.fill((255, 235, 0), (6, 12, 4, 7))
        s.fill((255, 235, 0), (6, 14, 8, 3))
        return s

    def _create_coin(self) -> pygame.Surface:
        s = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 215, 0), (9, 9), 8)
        pygame.draw.circle(s, (215, 165, 0), (9, 9), 6)
        pygame.draw.circle(s, (255, 255, 255), (7, 7), 2)
        return s

    def _create_nitro_bottle(self) -> pygame.Surface:
        s = pygame.Surface((16, 22), pygame.SRCALPHA)
        s.fill((0, 220, 255), (3, 5, 10, 16))
        s.fill((230, 240, 255), (5, 0, 6, 5))
        pygame.draw.rect(s, (10, 15, 25), (3, 5, 10, 16), 1)
        return s

    def _create_shield_orb(self) -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 128), (10, 10), 9)
        pygame.draw.circle(s, (255, 255, 255), (10, 10), 4)
        return s

    # -------------------------------------------------------------------------
    # DRIVER'S COCKPIT (Sleek 320x44 Molded Dashboard & Steering Wheel)
    # -------------------------------------------------------------------------
    def _create_cockpit_dashboard(self) -> pygame.Surface:
        s = pygame.Surface((320, 44), pygame.SRCALPHA)
        pts = [(0, 14), (55, 4), (265, 4), (320, 14), (320, 44), (0, 44)]
        pygame.draw.polygon(s, (22, 24, 32), pts)
        pygame.draw.lines(s, (55, 60, 75), False, pts[:4], 2)

        s.fill((12, 14, 18), (145, 8, 30, 6))
        for x in range(148, 172, 4):
            s.fill((48, 54, 65), (x, 9, 2, 4))
        pygame.draw.circle(s, (235, 45, 45), (160, 20), 3)

        s.fill((5, 15, 25), (142, 26, 36, 14))
        pygame.draw.rect(s, (0, 210, 255), (142, 26, 36, 14), 1)

        s.fill((10, 12, 18), (72, 6, 52, 26))
        pygame.draw.rect(s, (65, 75, 95), (72, 6, 52, 26), 1)
        return s

    def _create_pixel_steering_wheel(self) -> pygame.Surface:
        s = pygame.Surface((52, 52), pygame.SRCALPHA)
        cx, cy = 26, 26
        pygame.draw.circle(s, (32, 35, 45), (cx, cy), 22, 6)
        pygame.draw.circle(s, (70, 75, 90), (cx, cy), 22, 1)
        pygame.draw.circle(s, (70, 75, 90), (cx, cy), 17, 1)

        s.fill((240, 35, 45), (24, 4, 4, 6))

        pygame.draw.circle(s, (22, 24, 30), (cx, cy), 8)
        pygame.draw.circle(s, (0, 210, 255), (cx, cy), 8, 1)
        pygame.draw.circle(s, (255, 215, 0), (cx, cy), 2)

        pygame.draw.line(s, (50, 55, 68), (cx, cy), (6, cy), 4)
        pygame.draw.line(s, (50, 55, 68), (cx, cy), (46, cy), 4)
        pygame.draw.line(s, (50, 55, 68), (cx, cy), (cx, 46), 4)
        return s
