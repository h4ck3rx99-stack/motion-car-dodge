"""
=============================================================================
🛣️ 1990s 2D Pseudo-3D Raster Road Engine & Parallax Environment
=============================================================================
Renders discrete banded arcade skies, parallax mountain horizons, scanline
projected 4-lane highway, telephone poles with wires, and roadside buildings.
"""

import math
import pygame

from config import (
    ARCADE_HEIGHT,
    ARCADE_WIDTH,
    CAMERA_DEPTH,
    DRAW_DISTANCE,
    HORIZON_Y,
    LANES_COUNT,
    ROAD_WIDTH,
    SEGMENT_LENGTH,
    THEME_CITY_OUTSKIRTS,
    THEME_COUNTRYSIDE,
    THEME_NIGHT,
    THEME_RAINY,
    THEME_SUNSET,
)


class ScreenPoint:
    __slots__ = ("x", "y", "w", "scale")

    def __init__(self, x=0, y=0, w=0, scale=0):
        self.x = x
        self.y = y
        self.w = w
        self.scale = scale


class WorldPoint:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


class RoadSegment:
    """A slice of the 2D pseudo-3D highway."""

    def __init__(self, index: int):
        self.index = index
        self.p1_world = WorldPoint(0, 0, index * SEGMENT_LENGTH)
        self.p2_world = WorldPoint(0, 0, (index + 1) * SEGMENT_LENGTH)

        self.p1_screen = ScreenPoint()
        self.p2_screen = ScreenPoint()

        self.curve = 0.0
        self.is_even = ((index // 3) % 2 == 0)

        # Roadside 2D Pixel Sprite (sprite_key, side: -1 left / +1 right, offset_mult)
        self.side_sprites = []


class Highway:
    """Manages procedural track generation, 2D rasterization and parallax."""

    def __init__(self, sprite_factory):
        self.factory = sprite_factory
        self.segments = []
        self._generate_track()
        self.track_length = len(self.segments) * SEGMENT_LENGTH

    def _generate_track(self):
        self.segments.clear()

        def add_section(length: int, curve: float, hill_h: float):
            start_idx = len(self.segments)
            for i in range(length):
                seg = RoadSegment(start_idx + i)
                progress = math.sin(math.pi * (i / length))
                seg.curve = curve * progress

                y_val = hill_h * math.sin(math.pi * (i / length))
                seg.p1_world.y = y_val
                seg.p2_world.y = y_val

                idx = start_idx + i

                # Add diverse 1990s arcade scenery sprites along the roadside
                if idx % 8 == 0:
                    seg.side_sprites.append(("pine_tree", -1, 1.4))
                elif idx % 8 == 4:
                    seg.side_sprites.append(("pine_tree", 1, 1.4))

                if idx % 12 == 2:
                    seg.side_sprites.append(("telephone_pole", -1, 1.15))
                elif idx % 12 == 8:
                    seg.side_sprites.append(("telephone_pole", 1, 1.15))

                if idx % 16 == 6:
                    seg.side_sprites.append(("rock_boulder", -1, 1.25))
                elif idx % 16 == 14:
                    seg.side_sprites.append(("rock_boulder", 1, 1.25))

                # Occasional Buildings & Billboards
                if idx % 42 == 0:
                    seg.side_sprites.append(("billboard_1", 1, 1.6))
                elif idx % 42 == 20:
                    seg.side_sprites.append(("billboard_2", -1, 1.6))
                elif idx % 65 == 10:
                    seg.side_sprites.append(("gas_station", 1, 1.9))
                elif idx % 65 == 35:
                    seg.side_sprites.append(("diner", -1, 1.9))
                elif idx % 85 == 50:
                    seg.side_sprites.append(("warehouse", 1, 2.0))
                elif idx % 85 == 15:
                    seg.side_sprites.append(("farmhouse", -1, 2.0))
                elif idx % 35 == 5:
                    seg.side_sprites.append(("barrel", -1, 1.05))

                self.segments.append(seg)

        # Track Sequence
        add_section(180, 0.0, 0)
        add_section(220, 2.4, 450)
        add_section(160, 0.0, -250)
        add_section(280, -3.2, 700)
        add_section(200, 1.8, -350)
        add_section(250, -2.0, 500)
        add_section(300, 3.2, -450)
        add_section(220, -1.2, 300)
        add_section(350, 0.0, 0)

    def find_segment(self, z_pos: float) -> RoadSegment:
        wrapped_z = z_pos % self.track_length
        idx = int(wrapped_z / SEGMENT_LENGTH) % len(self.segments)
        return self.segments[idx]

    def project_point(
        self,
        world_p: WorldPoint,
        cam_x: float,
        cam_y: float,
        cam_z: float,
        cam_depth: float,
        sw: int,
        sh: int,
        rw: float
    ) -> ScreenPoint:
        trans_x = world_p.x - cam_x
        trans_y = world_p.y - cam_y
        trans_z = world_p.z - cam_z

        if trans_z <= 10.0:
            trans_z = 10.0

        scale = cam_depth / trans_z
        sx = int((sw / 2) + (scale * trans_x * (sw / 2)))
        sy = int(HORIZON_Y - (scale * trans_y * (sh / 2)))
        sw_width = int(scale * rw * (sw / 2))

        return ScreenPoint(sx, sy, sw_width, scale)

    # -------------------------------------------------------------------------
    # 2D BANDED ARCADE SKY & PARALLAX MOUNTAINS
    # -------------------------------------------------------------------------
    def render_backdrop(self, surface: pygame.Surface, cam_x: float, time_sec: float, theme: int):
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT
        horizon_y = HORIZON_Y

        # 1. Discrete Banded Arcade Sky
        if theme == THEME_COUNTRYSIDE:
            sky_bands = [
                ((40, 110, 215), 0, 22),
                ((65, 140, 235), 22, 45),
                ((100, 175, 245), 45, 68),
                ((160, 215, 255), 68, horizon_y),
            ]
            m1_col = (80, 110, 140)
            m2_col = (45, 90, 60)
            sun_col = (255, 230, 80)
            has_sun = True

        elif theme == THEME_SUNSET:
            sky_bands = [
                ((25, 15, 45), 0, 18),
                ((95, 30, 75), 18, 38),
                ((190, 45, 80), 38, 58),
                ((245, 110, 40), 58, 76),
                ((255, 195, 60), 76, horizon_y),
            ]
            m1_col = (60, 25, 50)
            m2_col = (40, 15, 35)
            sun_col = (255, 60, 110)
            has_sun = True

        elif theme == THEME_NIGHT:
            sky_bands = [
                ((6, 8, 18), 0, 25),
                ((14, 18, 36), 25, 50),
                ((28, 32, 60), 50, 72),
                ((45, 40, 75), 72, horizon_y),
            ]
            m1_col = (20, 24, 45)
            m2_col = (12, 16, 30)
            sun_col = (230, 240, 255)
            has_sun = True

        elif theme == THEME_RAINY:
            sky_bands = [
                ((45, 50, 60), 0, 25),
                ((65, 72, 85), 25, 55),
                ((90, 100, 115), 55, horizon_y),
            ]
            m1_col = (50, 58, 68)
            m2_col = (35, 42, 50)
            sun_col = None
            has_sun = False

        else:  # CITY_OUTSKIRTS
            sky_bands = [
                ((30, 40, 65), 0, 22),
                ((55, 70, 105), 22, 46),
                ((110, 95, 125), 46, 70),
                ((180, 140, 130), 70, horizon_y),
            ]
            m1_col = (45, 40, 60)
            m2_col = (30, 35, 45)
            sun_col = (255, 180, 70)
            has_sun = True

        for col, y1, y2 in sky_bands:
            pygame.draw.rect(surface, col, (0, y1, sw, y2 - y1 + 1))

        # 2. Pixel Arcade Sun / Moon
        if has_sun:
            sun_x = int(sw * 0.72 - cam_x * 0.04) % sw
            sun_y = int(horizon_y * 0.36)
            pygame.draw.circle(surface, sun_col, (sun_x, sun_y), 16)
            pygame.draw.circle(surface, (255, 255, 255), (sun_x, sun_y), 10)

        # 3. Chunky Pixel Clouds
        if theme != THEME_NIGHT:
            cloud_offset = int(time_sec * 12 + cam_x * 0.02) % sw
            for cx_base, cy_base in [(sw * 0.15, 16), (sw * 0.55, 28), (sw * 0.85, 12)]:
                cx = int((cx_base - cloud_offset) % sw)
                cy = int(cy_base)
                c_col = (245, 250, 255) if theme != THEME_RAINY else (140, 150, 165)
                pygame.draw.rect(surface, c_col, (cx, cy, 26, 8))
                pygame.draw.rect(surface, c_col, (cx + 5, cy - 5, 16, 12))
                pygame.draw.rect(surface, c_col, (cx + 14, cy - 3, 16, 10))

        # 4. Layer 1: Distant Jagged Mountains (Slower Parallax)
        m1_offset = int(cam_x * 0.08) % sw
        for ox in (-sw, 0, sw):
            pts1 = [
                (ox - m1_offset, horizon_y),
                (ox - m1_offset + int(sw * 0.18), horizon_y - 32),
                (ox - m1_offset + int(sw * 0.35), horizon_y - 16),
                (ox - m1_offset + int(sw * 0.55), horizon_y - 40),
                (ox - m1_offset + int(sw * 0.75), horizon_y - 18),
                (ox - m1_offset + int(sw * 0.90), horizon_y - 34),
                (ox - m1_offset + sw, horizon_y),
            ]
            pygame.draw.polygon(surface, m1_col, pts1)

        # 5. Layer 2: Near Forest / City Skyline (Faster Parallax)
        m2_offset = int(cam_x * 0.18) % sw
        for ox in (-sw, 0, sw):
            if theme == THEME_CITY_OUTSKIRTS or theme == THEME_NIGHT:
                for b_idx in range(16):
                    bx = ox + b_idx * 22 - m2_offset
                    bh = 12 + (b_idx * 7) % 22
                    pygame.draw.rect(surface, m2_col, (bx, horizon_y - bh, 18, bh))
                    if (b_idx % 2 == 0):
                        pygame.draw.rect(surface, (255, 230, 80), (bx + 4, horizon_y - bh + 4, 3, 3))
                        pygame.draw.rect(surface, (255, 230, 80), (bx + 11, horizon_y - bh + 4, 3, 3))
            else:
                pts2 = [
                    (ox - m2_offset, horizon_y),
                    (ox - m2_offset + int(sw * 0.12), horizon_y - 18),
                    (ox - m2_offset + int(sw * 0.28), horizon_y - 6),
                    (ox - m2_offset + int(sw * 0.48), horizon_y - 22),
                    (ox - m2_offset + int(sw * 0.68), horizon_y - 10),
                    (ox - m2_offset + int(sw * 0.85), horizon_y - 16),
                    (ox - m2_offset + sw, horizon_y),
                ]
                pygame.draw.polygon(surface, m2_col, pts2)

    # -------------------------------------------------------------------------
    # 2D RASTER ROAD & ROADSIDE SPRITE PROJECTION
    # -------------------------------------------------------------------------
    def render_road(
        self,
        surface: pygame.Surface,
        cam_x: float,
        cam_y: float,
        cam_z: float,
        theme: int,
        draw_dist: int = DRAW_DISTANCE
    ):
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT
        cam_depth = CAMERA_DEPTH

        start_seg = self.find_segment(cam_z)
        start_idx = start_seg.index

        dx = - (start_seg.curve * ((cam_z % SEGMENT_LENGTH) / SEGMENT_LENGTH))
        x = 0.0
        max_y = sh

        # Palette selection based on active theme
        if theme == THEME_COUNTRYSIDE:
            c_grass_1 = (55, 145, 45)
            c_grass_2 = (42, 125, 35)
            c_road_1 = (65, 68, 75)
            c_road_2 = (55, 58, 65)
            c_rumble_1 = (220, 35, 35)
            c_rumble_2 = (245, 245, 245)
            c_lane = (255, 255, 255)
            c_center = (255, 215, 0)

        elif theme == THEME_SUNSET:
            c_grass_1 = (95, 75, 35)
            c_grass_2 = (75, 58, 28)
            c_road_1 = (50, 42, 52)
            c_road_2 = (40, 34, 42)
            c_rumble_1 = (240, 70, 30)
            c_rumble_2 = (255, 210, 80)
            c_lane = (255, 220, 180)
            c_center = (255, 180, 40)

        elif theme == THEME_NIGHT:
            c_grass_1 = (12, 18, 15)
            c_grass_2 = (8, 12, 10)
            c_road_1 = (35, 38, 45)
            c_road_2 = (26, 28, 34)
            c_rumble_1 = (180, 20, 40)
            c_rumble_2 = (80, 85, 95)
            c_lane = (210, 220, 240)
            c_center = (240, 200, 0)

        elif theme == THEME_RAINY:
            c_grass_1 = (40, 95, 45)
            c_grass_2 = (30, 80, 35)
            c_road_1 = (45, 50, 60)
            c_road_2 = (38, 42, 50)
            c_rumble_1 = (180, 30, 30)
            c_rumble_2 = (200, 200, 210)
            c_lane = (230, 235, 245)
            c_center = (230, 190, 0)

        else: # CITY_OUTSKIRTS
            c_grass_1 = (48, 75, 40)
            c_grass_2 = (38, 62, 32)
            c_road_1 = (58, 60, 68)
            c_road_2 = (48, 50, 56)
            c_rumble_1 = (210, 40, 40)
            c_rumble_2 = (235, 235, 240)
            c_lane = (255, 255, 255)
            c_center = (255, 210, 0)

        sprites_to_render = []

        # 1. Rasterize Road Scanline Bands
        for n in range(draw_dist):
            idx = (start_idx + n) % len(self.segments)
            seg = self.segments[idx]

            seg_z1 = seg.p1_world.z
            if seg_z1 < cam_z:
                seg_z1 += self.track_length
            seg_z2 = seg.p2_world.z
            if seg_z2 < cam_z:
                seg_z2 += self.track_length

            w1 = WorldPoint(seg.p1_world.x - x, seg.p1_world.y, seg_z1)
            w2 = WorldPoint(seg.p2_world.x - x - dx, seg.p2_world.y, seg_z2)

            seg.p1_screen = self.project_point(w1, cam_x, cam_y, cam_z, cam_depth, sw, sh, ROAD_WIDTH)
            seg.p2_screen = self.project_point(w2, cam_x, cam_y, cam_z, cam_depth, sw, sh, ROAD_WIDTH)

            x += dx
            dx += seg.curve

            if seg.p1_screen.y < seg.p2_screen.y or seg.p1_screen.y <= HORIZON_Y:
                continue

            if seg.p2_screen.y >= max_y:
                continue

            c_grass = c_grass_1 if seg.is_even else c_grass_2
            c_road = c_road_1 if seg.is_even else c_road_2
            c_rumble = c_rumble_1 if seg.is_even else c_rumble_2

            # Grass Shoulder Background
            pygame.draw.rect(
                surface,
                c_grass,
                (0, seg.p2_screen.y, sw, min(max_y, seg.p1_screen.y) - seg.p2_screen.y + 1)
            )

            # Red/White Curbs
            rumble_w1 = int(seg.p1_screen.w * 1.15)
            rumble_w2 = int(seg.p2_screen.w * 1.15)
            self._draw_poly(surface, c_rumble, seg.p1_screen.x, seg.p1_screen.y, rumble_w1, seg.p2_screen.x, seg.p2_screen.y, rumble_w2)

            # Dark Asphalt Road
            self._draw_poly(surface, c_road, seg.p1_screen.x, seg.p1_screen.y, seg.p1_screen.w, seg.p2_screen.x, seg.p2_screen.y, seg.p2_screen.w)

            # Lane Markings
            if seg.is_even:
                lane_w1 = seg.p1_screen.w * 2 / LANES_COUNT
                lane_w2 = seg.p2_screen.w * 2 / LANES_COUNT
                for lane in range(1, LANES_COUNT):
                    lx1 = int(seg.p1_screen.x - seg.p1_screen.w + lane_w1 * lane)
                    lx2 = int(seg.p2_screen.x - seg.p2_screen.w + lane_w2 * lane)
                    lw1 = max(1, int(seg.p1_screen.w * 0.022))
                    lw2 = max(1, int(seg.p2_screen.w * 0.022))

                    if lane == LANES_COUNT // 2:
                        # Double Yellow Center Line
                        self._draw_poly(surface, c_center, lx1 - lw1 * 2, seg.p1_screen.y, lw1, lx2 - lw2 * 2, seg.p2_screen.y, lw2)
                        self._draw_poly(surface, c_center, lx1 + lw1 * 2, seg.p1_screen.y, lw1, lx2 + lw2 * 2, seg.p2_screen.y, lw2)
                    else:
                        self._draw_poly(surface, c_lane, lx1, seg.p1_screen.y, lw1, lx2, seg.p2_screen.y, lw2)

            # Collect Roadside Sprites for this segment
            for sp_name, side, off_mult in seg.side_sprites:
                sprites_to_render.append((sp_name, side, off_mult, seg.p1_screen))

            max_y = seg.p2_screen.y

        # 2. Render Roadside 2D Sprites in Depth Order (Farthest to Nearest)
        sprites_to_render.reverse()
        for sp_name, side, off_mult, s_pt in sprites_to_render:
            scale = s_pt.scale
            if scale < 0.0006 or sp_name not in self.factory.sprites:
                continue

            base_sprite = self.factory.sprites[sp_name]
            orig_w, orig_h = base_sprite.get_size()

            scaled_w = max(2, int(orig_w * scale * 2.5))
            scaled_h = max(2, int(orig_h * scale * 2.5))

            if scaled_w < 2 or scaled_h < 2:
                continue

            sp_img = pygame.transform.scale(base_sprite, (scaled_w, scaled_h))

            sp_x = int(s_pt.x + side * (s_pt.w * off_mult))
            sp_y = s_pt.y

            surface.blit(sp_img, (sp_x - scaled_w // 2, sp_y - scaled_h))

    def _draw_poly(self, surface, color, x1, y1, w1, x2, y2, w2):
        pts = [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)]
        pygame.draw.polygon(surface, color, pts)
