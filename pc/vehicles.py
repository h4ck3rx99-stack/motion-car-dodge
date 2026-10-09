"""
=============================================================================
🚗 1990s 2D Sprite-Based Traffic & Dynamic Traffic Density Wave Engine
=============================================================================
Right-hand drive highway system: Left lanes (0 & 1) have oncoming traffic
heading toward player; Right lanes (2 & 3) have same-direction cruising traffic.
Spawns vehicles far on the distant horizon with smooth, balanced approach speeds.
"""

import math
import random
import pygame

from config import (
    ARCADE_HEIGHT,
    ARCADE_WIDTH,
    BASE_MAX_SPEED,
    BASE_MIN_SPEED,
    CAMERA_DEPTH,
    FUEL_BURN_RATE,
    FUEL_PICKUP_AMOUNT,
    HORIZON_Y,
    LANES_COUNT,
    MAX_FUEL,
    MAX_ROAD_BOUND,
    NITRO_MAX_SPEED,
    ROAD_WIDTH,
    SEGMENT_LENGTH,
)


class VehicleType:
    SPORTS = "car_sports"
    SEDAN = "car_sedan"
    TRUCK = "car_truck"
    VAN = "car_van"
    BUS = "car_bus"
    BIKE = "car_bike"


class CollectibleType:
    FUEL = "item_fuel"
    COIN = "item_coin"
    NITRO = "item_nitro"
    SHIELD = "item_shield"


class TrafficCar:
    """An AI traffic car on the highway."""

    def __init__(self, z: float, lane: int, is_oncoming: bool, sprite_key: str = None):
        self.z = z
        self.lane = lane
        self.is_oncoming = is_oncoming

        if sprite_key is None:
            sprite_key = random.choice([
                VehicleType.SPORTS,
                VehicleType.SEDAN,
                VehicleType.TRUCK,
                VehicleType.VAN,
                VehicleType.BUS,
                VehicleType.BIKE,
            ])
        self.sprite_key = sprite_key

        # Lane to lateral X coordinate (-1.0 to 1.0)
        lane_w = 2.0 / LANES_COUNT
        self.x = -1.0 + (lane + 0.5) * lane_w

        # Balanced AI speeds
        if sprite_key == VehicleType.TRUCK:
            base_s = 40.0
        elif sprite_key == VehicleType.BUS:
            base_s = 45.0
        elif sprite_key == VehicleType.SPORTS:
            base_s = 85.0
        elif sprite_key == VehicleType.BIKE:
            base_s = 75.0
        else:
            base_s = 58.0

        # Left lanes drive towards player (negative speed), Right lanes drive forward (positive speed)
        self.speed = -base_s if is_oncoming else base_s
        self.active = True
        self.has_triggered_near_miss = False

    def update(self, dt: float, track_length: float):
        world_speed = self.speed * 20.0
        self.z += world_speed * dt

        if self.z < 0:
            self.z += track_length
        elif self.z >= track_length:
            self.z -= track_length


class CollectibleItem:
    """A collectible pickup floating above the road."""

    def __init__(self, z: float, lane: int, item_type: str):
        self.z = z
        self.lane = lane
        self.item_type = item_type
        lane_w = 2.0 / LANES_COUNT
        self.x = -1.0 + (lane + 0.5) * lane_w
        self.active = True
        self.anim_t = random.uniform(0, 6.28)

    def update(self, dt: float):
        self.anim_t += dt * 4.0


class PlayerCar:
    """The player's sports car physics and state."""

    def __init__(self):
        # Start on the right side of the road (Lane 2)
        self.x = 0.35
        self.z = 0.0
        self.speed = BASE_MIN_SPEED
        self.steering_angle = 0.0

        self.fuel = MAX_FUEL
        self.nitro_charge = 100.0
        self.is_nitro_active = False
        self.is_braking = False
        self.shield_timer = 0.0

        self.lives = 3
        self.score = 0
        self.distance_miles = 0.0
        self.near_miss_combo = 0
        self.combo_timer = 0.0
        self.top_speed = BASE_MIN_SPEED
        self.fuel_alert_timer = 0.0

    def update(
        self,
        dt: float,
        steer_input: float,
        nitro_req: bool,
        brake_req: bool,
        track_length: float
    ):
        self.steering_angle = steer_input

        # Fuel Consumption
        self.fuel = max(0.0, self.fuel - FUEL_BURN_RATE * dt)
        if self.fuel <= 0:
            self.speed = max(0.0, self.speed - 40.0 * dt)
            if self.speed <= 0:
                self.lives = 0
            return

        if self.fuel_alert_timer > 0:
            self.fuel_alert_timer = max(0.0, self.fuel_alert_timer - dt)

        # Nitro & Throttle
        if nitro_req and self.nitro_charge > 0 and not brake_req:
            self.is_nitro_active = True
            self.nitro_charge = max(0.0, self.nitro_charge - 24.0 * dt)
            target_max = NITRO_MAX_SPEED
            accel = 55.0
        else:
            self.is_nitro_active = False
            self.nitro_charge = min(100.0, self.nitro_charge + 8.5 * dt)
            target_max = BASE_MAX_SPEED
            accel = 35.0

        self.is_braking = brake_req
        if brake_req:
            self.speed = max(BASE_MIN_SPEED * 0.4, self.speed - 80.0 * dt)
        else:
            if self.speed < target_max:
                self.speed = min(target_max, self.speed + accel * dt)
            elif self.speed > target_max:
                self.speed = max(target_max, self.speed - 25.0 * dt)

        # Snappy Lateral Steering
        speed_mult = max(0.5, self.speed / BASE_MAX_SPEED)
        self.x += steer_input * 4.4 * speed_mult * dt
        self.x = max(-MAX_ROAD_BOUND, min(MAX_ROAD_BOUND, self.x))

        if abs(self.x) > 1.05:
            self.speed = max(30.0, self.speed - 45.0 * dt)

        # Forward Distance Travel
        dist_delta = (self.speed * 20.0) * dt
        self.z = (self.z + dist_delta) % track_length
        self.distance_miles += (self.speed * dt) / 3600.0

        if self.speed > self.top_speed:
            self.top_speed = self.speed

        if self.shield_timer > 0:
            self.shield_timer = max(0.0, self.shield_timer - dt)

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.near_miss_combo = 0


class VehicleManager:
    """Manages dynamic traffic waves, right-hand drive traffic, and distant spawning."""

    def __init__(self, highway, sprite_factory):
        self.highway = highway
        self.factory = sprite_factory
        self.traffic = []
        self.collectibles = []
        self.wave_time = 0.0
        self.current_target_cars = 3
        self._populate_initial()

    def _populate_initial(self):
        # Start with 3 cars spawned far on the distant horizon
        # Lanes 0 & 1: Oncoming traffic; Lanes 2 & 3: Same-direction traffic
        initial_configs = [
            (2400.0, 0, True),   # Oncoming car in far-left lane
            (3600.0, 2, False),  # Same-direction cruising car in right lane
            (4800.0, 1, True),   # Oncoming car in inner-left lane
        ]
        for z, lane, is_oncoming in initial_configs:
            self.traffic.append(TrafficCar(z, lane, is_oncoming))

        # Initial fuel cans & pickups placed far down the road
        for i in range(6):
            z = 1200.0 + i * 850.0
            lane = (i * 2 + 1) % LANES_COUNT
            itype = CollectibleType.FUEL if i % 2 == 0 else random.choice([
                CollectibleType.COIN, CollectibleType.NITRO, CollectibleType.SHIELD
            ])
            self.collectibles.append(CollectibleItem(z, lane, itype))

    def _get_staggered_spawn_z(self, player_z: float, track_length: float, lane: int) -> float:
        """Spawns vehicles far on the distant horizon with good spacing."""
        base_dist = random.uniform(2200.0, 6200.0)
        candidate_z = (player_z + base_dist) % track_length

        for c in self.traffic:
            if c.lane == lane:
                dz = abs(c.z - candidate_z)
                if dz < 350.0:
                    candidate_z = (candidate_z + 400.0) % track_length
                    break
        return candidate_z

    def update(self, dt: float, player: PlayerCar, track_length: float, sounds):
        self.wave_time += dt

        # ---------------------------------------------------------------------
        # 1. GENTLE START & DYNAMIC WAVE CALCULATION
        # ---------------------------------------------------------------------
        if self.wave_time < 12.0:
            warmup_ratio = self.wave_time / 12.0
            self.current_target_cars = int(3 + 4 * warmup_ratio)
        else:
            wave_phase = (self.wave_time - 12.0)
            wave_sine = math.sin(wave_phase * (2 * math.pi / 36.0))
            dist_bonus = min(3, int(player.distance_miles * 1.0))

            min_cars = 4 + dist_bonus
            max_cars = 15 + dist_bonus
            self.current_target_cars = int(min_cars + (max_cars - min_cars) * (0.5 + 0.5 * wave_sine))

        # ---------------------------------------------------------------------
        # 2. UPDATE & RECYCLE TRAFFIC VEHICLES INFINITELY
        # ---------------------------------------------------------------------
        surviving_traffic = []
        for car in self.traffic:
            car.update(dt, track_length)
            rel_z = car.z - player.z
            if rel_z > track_length / 2:
                rel_z -= track_length
            elif rel_z < -track_length / 2:
                rel_z += track_length

            # Recycle cars that passed behind player
            if rel_z < -220.0 or not car.active:
                if len(surviving_traffic) + len(self.traffic) - len(surviving_traffic) > self.current_target_cars:
                    continue

                car.lane = random.randint(0, LANES_COUNT - 1)
                # Left lanes (0, 1) = Oncoming; Right lanes (2, 3) = Forward traffic
                car.is_oncoming = (car.lane < LANES_COUNT // 2)
                car.z = self._get_staggered_spawn_z(player.z, track_length, car.lane)
                lane_w = 2.0 / LANES_COUNT
                car.x = -1.0 + (car.lane + 0.5) * lane_w
                car.sprite_key = random.choice([
                    VehicleType.SPORTS,
                    VehicleType.SEDAN,
                    VehicleType.TRUCK,
                    VehicleType.VAN,
                    VehicleType.BUS,
                    VehicleType.BIKE,
                ])

                # Reset speed based on lane direction
                if car.sprite_key == VehicleType.TRUCK:
                    base_s = 40.0
                elif car.sprite_key == VehicleType.BUS:
                    base_s = 45.0
                elif car.sprite_key == VehicleType.SPORTS:
                    base_s = 85.0
                elif car.sprite_key == VehicleType.BIKE:
                    base_s = 75.0
                else:
                    base_s = 58.0
                car.speed = -base_s if car.is_oncoming else base_s

                car.has_triggered_near_miss = False
                car.active = True
                surviving_traffic.append(car)
            else:
                surviving_traffic.append(car)

        self.traffic = surviving_traffic

        # Spawn up to current target
        while len(self.traffic) < self.current_target_cars:
            lane = random.randint(0, LANES_COUNT - 1)
            is_oncoming = (lane < LANES_COUNT // 2)
            sz = self._get_staggered_spawn_z(player.z, track_length, lane)
            self.traffic.append(TrafficCar(sz, lane, is_oncoming))

        # ---------------------------------------------------------------------
        # 3. UPDATE & RECYCLE FUEL CANS & POWERUPS INFINITELY
        # ---------------------------------------------------------------------
        for item in self.collectibles:
            item.update(dt)
            rel_z = item.z - player.z
            if rel_z > track_length / 2:
                rel_z -= track_length
            elif rel_z < -track_length / 2:
                rel_z += track_length

            if rel_z < -180.0 or not item.active:
                item.lane = random.randint(0, LANES_COUNT - 1)
                item.z = (player.z + random.uniform(1600.0, 5200.0)) % track_length
                lane_w = 2.0 / LANES_COUNT
                item.x = -1.0 + (item.lane + 0.5) * lane_w

                if player.fuel < 60.0 or random.random() < 0.65:
                    item.item_type = CollectibleType.FUEL
                else:
                    item.item_type = random.choice([
                        CollectibleType.COIN, CollectibleType.NITRO, CollectibleType.SHIELD
                    ])
                item.active = True

        while len(self.collectibles) < 7:
            lane = random.randint(0, LANES_COUNT - 1)
            sz = (player.z + random.uniform(1800.0, 4800.0)) % track_length
            self.collectibles.append(CollectibleItem(sz, lane, CollectibleType.FUEL))

        # 4. Collisions
        self._check_collisions(player, sounds, track_length)

    def _check_collisions(self, player: PlayerCar, sounds, track_length: float):
        for car in self.traffic:
            if not car.active:
                continue
            rel_z = car.z - player.z
            if rel_z > track_length / 2:
                rel_z -= track_length
            elif rel_z < -track_length / 2:
                rel_z += track_length

            dx = abs(car.x - player.x)
            dz = abs(rel_z)

            # Hitbox collision
            if dz < 140.0 and dx < 0.38:
                if player.shield_timer <= 0:
                    player.lives -= 1
                    player.speed = BASE_MIN_SPEED * 0.4
                    player.near_miss_combo = 0
                    sounds.play("crash", 0.8)
                    car.active = False
                else:
                    car.active = False
                    player.score += 250
                    sounds.play("crash", 0.5)

            # Close Call Near-Miss detection
            elif dz < 120.0 and dx < 0.52 and not car.has_triggered_near_miss:
                car.has_triggered_near_miss = True
                player.near_miss_combo += 1
                player.combo_timer = 3.5
                bonus = 150 * min(5, player.near_miss_combo)
                player.score += bonus
                player.nitro_charge = min(100.0, player.nitro_charge + 25.0)
                sounds.play("near_miss", 0.6)

        # Collectibles
        for item in self.collectibles:
            if not item.active:
                continue
            rel_z = item.z - player.z
            if rel_z > track_length / 2:
                rel_z -= track_length
            elif rel_z < -track_length / 2:
                rel_z += track_length

            dx = abs(item.x - player.x)
            dz = abs(rel_z)

            if dz < 170.0 and dx < 0.40:
                item.active = False
                sounds.play("pickup", 0.7)
                if item.item_type == CollectibleType.FUEL:
                    player.fuel = min(MAX_FUEL, player.fuel + FUEL_PICKUP_AMOUNT)
                    player.score += 200
                    player.fuel_alert_timer = 1.6
                elif item.item_type == CollectibleType.COIN:
                    player.score += 500
                elif item.item_type == CollectibleType.NITRO:
                    player.nitro_charge = 100.0
                    player.score += 100
                elif item.item_type == CollectibleType.SHIELD:
                    player.shield_timer = 8.0
                    player.score += 300

    def render_traffic_and_items(
        self,
        surface: pygame.Surface,
        cam_x: float,
        cam_y: float,
        cam_z: float,
        track_length: float
    ):
        """Projects and scales 2D pixel-art traffic vehicles and pickups."""
        sw = ARCADE_WIDTH
        sh = ARCADE_HEIGHT
        cam_depth = CAMERA_DEPTH

        render_list = []

        for car in self.traffic:
            if not car.active:
                continue
            rel_z = (car.z - cam_z)
            if rel_z < 0:
                rel_z += track_length
            if 30 < rel_z < 9500:
                seg = self.highway.find_segment(car.z)
                wx = car.x * (ROAD_WIDTH / 2)
                wy = seg.p1_world.y
                render_list.append(("car", car, wx, wy, rel_z))

        for item in self.collectibles:
            if not item.active:
                continue
            rel_z = (item.z - cam_z)
            if rel_z < 0:
                rel_z += track_length
            if 30 < rel_z < 9500:
                seg = self.highway.find_segment(item.z)
                wx = item.x * (ROAD_WIDTH / 2)
                wy = seg.p1_world.y + 25.0 + math.sin(item.anim_t) * 10.0
                render_list.append(("item", item, wx, wy, rel_z))

        render_list.sort(key=lambda x: x[4], reverse=True)

        for itype, obj, wx, wy, rz in render_list:
            scale = cam_depth / rz
            sx = int((sw / 2) + (scale * (wx - cam_x) * (sw / 2)))
            sy = int(HORIZON_Y - (scale * (wy - cam_y) * (sh / 2)))

            if itype == "car":
                self._draw_pixel_car_sprite(surface, obj, sx, sy, scale)
            elif itype == "item":
                self._draw_pixel_item_sprite(surface, obj, sx, sy, scale)

    def _draw_pixel_car_sprite(self, surface: pygame.Surface, car: TrafficCar, sx: int, sy: int, scale: float):
        if car.sprite_key not in self.factory.sprites:
            return

        base_sprite = self.factory.sprites[car.sprite_key]
        orig_w, orig_h = base_sprite.get_size()

        # 2D Sprite Scale
        scaled_w = max(4, int(scale * 300.0 * (ARCADE_WIDTH / 2)))
        scaled_h = max(3, int(scaled_w * (orig_h / orig_w)))

        if scaled_w < 3 or scaled_h < 2:
            return

        shadow_w = int(scaled_w * 1.15)
        shadow_h = max(2, int(scaled_h * 0.35))
        pygame.draw.ellipse(surface, (12, 14, 18), (sx - shadow_w // 2, sy - shadow_h // 2, shadow_w, shadow_h))

        scaled_sprite = pygame.transform.scale(base_sprite, (scaled_w, scaled_h))

        if car.is_oncoming:
            surface.blit(scaled_sprite, (sx - scaled_w // 2, sy - scaled_h))
            hl_sz = max(2, scaled_w // 6)
            pygame.draw.rect(surface, (255, 255, 200), (sx - scaled_w // 2 + 2, sy - max(2, scaled_h // 3), hl_sz, max(2, hl_sz // 2)))
            pygame.draw.rect(surface, (255, 255, 200), (sx + scaled_w // 2 - hl_sz - 2, sy - max(2, scaled_h // 3), hl_sz, max(2, hl_sz // 2)))
        else:
            surface.blit(scaled_sprite, (sx - scaled_w // 2, sy - scaled_h))

    def _draw_pixel_item_sprite(self, surface: pygame.Surface, item: CollectibleItem, sx: int, sy: int, scale: float):
        if item.item_type not in self.factory.sprites:
            return

        base_sprite = self.factory.sprites[item.item_type]
        orig_w, orig_h = base_sprite.get_size()

        scaled_w = max(6, int(scale * 240.0 * (ARCADE_WIDTH / 2)))
        scaled_h = max(6, int(scaled_w * (orig_h / orig_w)))

        if scaled_w < 4 or scaled_h < 4:
            return

        pygame.draw.ellipse(surface, (15, 18, 24), (sx - scaled_w // 2, sy + 2, scaled_w, max(2, scaled_h // 4)))

        scaled_sprite = pygame.transform.scale(base_sprite, (scaled_w, scaled_h))
        surface.blit(scaled_sprite, (sx - scaled_w // 2, sy - scaled_h))
