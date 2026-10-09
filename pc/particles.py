"""
=============================================================================
✨ High-Res Visual Effects, Particle Systems & Warp Speed Lines
=============================================================================
Renders exhaust flames, nitro trails, tire skids, crash explosions,
and warp speed lines.
"""

import math
import random
import pygame

from config import (
    COLOR_NEON_CYAN,
    COLOR_NEON_PINK,
    COLOR_NEON_YELLOW,
)


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "alpha", "gravity")

    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.alpha = 255
        self.gravity = gravity

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        if self.max_life > 0:
            self.alpha = max(0, int(255 * (self.life / self.max_life)))
        return self.life > 0


class ParticleSystem:
    """Manages all game visual particle effects."""

    def __init__(self):
        self.particles = []
        self.speed_lines = []
        self._init_speed_lines()

    def _init_speed_lines(self):
        for _ in range(50):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(250, 950)
            self.speed_lines.append({
                "angle": angle,
                "dist": dist,
                "speed": random.uniform(500, 1300),
                "len": random.uniform(40, 120),
            })

    def emit_exhaust(self, x: float, y: float, is_nitro: bool, count: int = 3):
        for _ in range(count):
            vx = random.uniform(-35, 35)
            vy = random.uniform(50, 160)
            life = random.uniform(0.15, 0.35)
            size = random.uniform(4, 9) if not is_nitro else random.uniform(8, 18)

            if is_nitro:
                col = random.choice([COLOR_NEON_CYAN, (180, 240, 255), (0, 140, 255)])
            else:
                col = random.choice([(255, 120, 20), (255, 60, 20), COLOR_NEON_YELLOW])

            self.particles.append(Particle(x, y, vx, vy, life, col, size))

    def emit_skid_smoke(self, x: float, y: float, count: int = 2):
        for _ in range(count):
            vx = random.uniform(-50, 50)
            vy = random.uniform(-15, 15)
            life = random.uniform(0.2, 0.45)
            size = random.uniform(6, 16)
            col = (210, 210, 225)
            self.particles.append(Particle(x, y, vx, vy, life, col, size, gravity=-20.0))

    def emit_crash_explosion(self, x: float, y: float, count: int = 40):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(120, 550)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.4, 0.9)
            size = random.uniform(5, 18)
            col = random.choice([(255, 40, 40), (255, 180, 20), (245, 245, 255), COLOR_NEON_PINK])
            self.particles.append(Particle(x, y, vx, vy, life, col, size, gravity=200.0))

    def update_and_render(self, surface: pygame.Surface, dt: float, car_speed: float, is_nitro: bool):
        sw = surface.get_width()
        sh = surface.get_height()

        surviving = []
        for p in self.particles:
            if p.update(dt):
                surviving.append(p)
                p_surf = pygame.Surface((int(p.size * 2), int(p.size * 2)), pygame.SRCALPHA)
                r, g, b = p.color
                pygame.draw.circle(p_surf, (r, g, b, p.alpha), (int(p.size), int(p.size)), int(p.size))
                surface.blit(p_surf, (int(p.x - p.size), int(p.y - p.size)))
        self.particles = surviving

        # Warp Speed Lines
        if car_speed > 130.0 or is_nitro:
            cx = sw // 2
            cy = sh // 2
            speed_mult = 1.9 if is_nitro else 1.0
            line_alpha = min(220, int((car_speed - 110) * 2.5)) if not is_nitro else 240

            for sl in self.speed_lines:
                sl["dist"] += sl["speed"] * speed_mult * dt
                if sl["dist"] > max(cx, cy) * 1.4:
                    sl["dist"] = random.uniform(200, 400)
                    sl["angle"] = random.uniform(0, math.pi * 2)

                x1 = cx + math.cos(sl["angle"]) * sl["dist"]
                y1 = cy + math.sin(sl["angle"]) * sl["dist"]
                x2 = cx + math.cos(sl["angle"]) * (sl["dist"] + sl["len"] * speed_mult)
                y2 = cy + math.sin(sl["angle"]) * (sl["dist"] + sl["len"] * speed_mult)

                col = (220, 250, 255) if not is_nitro else COLOR_NEON_CYAN
                pygame.draw.line(surface, col, (int(x1), int(y1)), (int(x2), int(y2)), 2 if is_nitro else 1)
