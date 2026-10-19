import math
import random
import pygame

pygame.init()

# =====================================================
# GAME SETTINGS
# =====================================================

WIDTH, HEIGHT = 1100, 650
GROUND_Y = 540
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fire vs Water")
clock = pygame.time.Clock()

WHITE = (245, 250, 255)
BLACK = (15, 18, 30)
BG = (12, 16, 35)
GROUND = (28, 35, 57)

FIRE_MAIN = (235, 55, 25)
FIRE_COLORS = [
    (255, 70, 20),
    (255, 135, 25),
    (255, 205, 55),
    (255, 245, 190),
]

WATER_MAIN = (25, 105, 230)
WATER_COLORS = [
    (20, 80, 230),
    (25, 170, 255),
    (100, 225, 255),
    (220, 250, 255),
]

FONT = pygame.font.SysFont("arial", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 16)


# =====================================================
# VISUAL HELPERS
# =====================================================

def draw_glow(surface, x, y, radius, color, alpha=100):
    radius = max(1, int(radius))

    glow = pygame.Surface(
        (radius * 6, radius * 6),
        pygame.SRCALPHA,
    )

    cx = cy = radius * 3

    for i in range(5, 0, -1):
        r = max(1, int(radius * i * 0.6))
        a = max(1, int(alpha / (i * 1.5)))

        pygame.draw.circle(
            glow,
            (*color, min(255, a)),
            (cx, cy),
            r,
        )

    surface.blit(
        glow,
        (int(x - cx), int(y - cy)),
        special_flags=pygame.BLEND_RGBA_ADD,
    )


def draw_background(surface, t):
    surface.fill(BG)

    for i in range(12):
        x = i * (WIDTH // 11)
        y = 100 + math.sin(t + i * 0.8) * 25

        pygame.draw.circle(
            surface,
            (20, 30, 65),
            (int(x), int(y)),
            55,
        )

    pygame.draw.rect(
        surface,
        GROUND,
        (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y),
    )

    pygame.draw.line(
        surface,
        (90, 115, 160),
        (0, GROUND_Y),
        (WIDTH, GROUND_Y),
        3,
    )

    for x in range(0, WIDTH, 55):
        pygame.draw.line(
            surface,
            (38, 48, 72),
            (x, GROUND_Y + 3),
            (x - 35, HEIGHT),
            1,
        )


# =====================================================
# PARTICLE CLASS
# =====================================================

class Particle:
    def __init__(
        self,
        x,
        y,
        color,
        size,
        lifetime,
        vx=0,
        vy=0,
    ):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx = vx
        self.vy = vy

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vx *= 0.985
        self.vy *= 0.985

        self.lifetime -= 1
        self.size *= 0.97

    def draw(self, surface):
        if self.lifetime <= 0:
            return

        radius = max(1, int(self.size))

        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            radius,
        )

    def is_dead(self):
        return self.lifetime <= 0 or self.size < 0.5


# =====================================================
# PROJECTILE CLASS
# =====================================================

class Projectile:
    def __init__(
        self,
        x,
        y,
        direction,
        is_fire,
        charged=False,
        vy=0,
        radius=10,
        damage=10,
    ):
        self.x = float(x)
        self.y = float(y)

        self.direction = direction
        self.is_fire = is_fire
        self.charged = charged

        self.speed = 10 if not charged else 14
        self.radius = radius if not charged else 16
        self.damage = damage if not charged else 20
        self.vy = vy
        self.timer = 100

        self.color = (
            FIRE_MAIN if is_fire else WATER_MAIN
        )

        self.colors = (
            FIRE_COLORS if is_fire else WATER_COLORS
        )

        self.rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, particles):
        self.x += self.direction * self.speed
        self.y += self.vy
        self.timer -= 1

        self.rect.center = (
            int(self.x),
            int(self.y),
        )

        if random.random() < 0.8:
            particles.append(
                Particle(
                    self.x - self.direction * self.radius * 0.5,
                    self.y + random.uniform(-4, 4),
                    random.choice(self.colors),
                    random.randint(2, 5),
                    14,
                    -self.direction * random.uniform(0.5, 2),
                    random.uniform(-1, 1),
                )
            )

    def draw(self, surface):
        draw_glow(
            surface,
            self.x,
            self.y,
            self.radius * 2,
            self.color,
            100,
        )

        if self.is_fire:
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                self.radius,
            )

            pygame.draw.circle(
                surface,
                WHITE,
                (int(self.x), int(self.y)),
                max(2, self.radius // 3),
            )
        else:
            # Wavy water trail / flowing wave crests for blue side attacks
            points = []
            for i in range(12):
                fraction = i / 11
                px = self.x - self.direction * (fraction * self.radius * 2.2)
                wave = math.sin(self.timer * 0.6 + fraction * math.pi * 3)
                py = self.y + wave * (self.radius * 0.75)
                points.append((int(px), int(py)))

            if len(points) >= 2:
                pygame.draw.lines(
                    surface,
                    self.colors[1] if len(self.colors) > 1 else self.color,
                    False,
                    points,
                    max(2, self.radius // 2),
                )

            # Water droplet head
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                self.radius,
            )

            pygame.draw.circle(
                surface,
                WHITE,
                (int(self.x), int(self.y)),
                max(2, self.radius // 3),
            )

    def is_finished(self):
        return (
            self.timer <= 0
            or self.x < -100
            or self.x > WIDTH + 100
            or self.y < 0
            or self.y > HEIGHT
        )


# =====================================================
# BEAM CLASS
# =====================================================

class Beam:
    def __init__(self, player):
        self.player = player
        self.is_fire = player.is_fire
        self.direction = player.direction

        self.x, self.y = player.get_hand_position()

        self.length = 700
        self.max_width = 34
        self.min_width = 8

        self.timer = 24
        self.max_timer = self.timer

        self.damage = 30
        self.hit_targets = set()

        self.animation_time = random.random() * math.tau
        self.particle_timer = 0

        self.colors = (
            FIRE_COLORS if self.is_fire
            else WATER_COLORS
        )

        self.main_color = (
            FIRE_MAIN if self.is_fire
            else WATER_MAIN
        )

        self.highlight = self.colors[-1]

        self.rect = pygame.Rect(
            int(self.x),
            int(self.y - self.max_width // 2),
            self.length,
            self.max_width,
        )

        if self.direction < 0:
            self.rect.left = int(self.x - self.length)

    def update(self, particles):
        if self.timer <= 0:
            return

        self.animation_time += 0.25
        self.particle_timer += 1
        self.timer -= 1

        self.rect.width = self.length
        self.rect.height = self.max_width
        self.rect.centery = int(self.y)

        if self.direction >= 0:
            self.rect.left = int(self.x)
        else:
            self.rect.right = int(self.x)

        if self.particle_timer % 2 == 0:
            count = 3 if self.is_fire else 2

            for _ in range(count):
                distance = random.uniform(0, self.length)

                px = self.x + self.direction * distance

                py = self.y + random.uniform(
                    -self.max_width * 0.5,
                    self.max_width * 0.5,
                )

                if self.is_fire:
                    vx = random.uniform(-1.5, 1.5)
                    vy = random.uniform(-2.5, 0.5)
                    size = random.randint(2, 6)
                    lifetime = 12
                else:
                    vx = -self.direction * random.uniform(0, 1)
                    vy = random.uniform(-1.2, 1.2)
                    size = random.randint(2, 5)
                    lifetime = 18

                particles.append(
                    Particle(
                        px,
                        py,
                        random.choice(self.colors),
                        size,
                        lifetime,
                        vx,
                        vy,
                    )
                )

    def draw(self, surface):
        if self.timer <= 0:
            return

        progress = max(
            0.0,
            min(1.0, self.timer / self.max_timer),
        )

        fade = min(
            1.0,
            (1.0 - progress) * 5 + 0.25,
        )

        pulse = (
            1.0
            + math.sin(self.animation_time * 2) * 0.08
        )

        beam_width = max(
            self.min_width,
            int(self.max_width * fade * pulse),
        )

        start_x = int(self.x)
        end_x = int(
            self.x + self.direction * self.length
        )
        center_y = int(self.y)

        # Outer glow.
        for i in range(12):
            fraction = (i + 1) / 12

            glow_x = (
                self.x
                + self.direction * self.length * fraction
            )

            glow_radius = max(
                3,
                int(beam_width * (1 - fraction * 0.45)),
            )

            draw_glow(
                surface,
                glow_x,
                self.y,
                glow_radius,
                self.main_color,
                int(75 * fade),
            )

        # Main beam.
        pygame.draw.line(
            surface,
            self.main_color,
            (start_x, center_y),
            (end_x, center_y),
            beam_width,
        )

        if self.is_fire:
            for i in range(15):
                fraction = i / 15

                px = (
                    self.x
                    + self.direction * self.length * fraction
                )

                wave = math.sin(
                    self.animation_time * 3 + i * 1.7
                )

                py = center_y + wave * beam_width * 0.45

                pygame.draw.circle(
                    surface,
                    random.choice(self.colors),
                    (int(px), int(py)),
                    random.randint(
                        2,
                        max(3, beam_width // 5),
                    ),
                )

        else:
            for band in range(3):
                points = []

                for i in range(25):
                    fraction = i / 24

                    px = (
                        self.x
                        + self.direction * self.length * fraction
                    )

                    wave = math.sin(
                        self.animation_time * 2
                        + fraction * 14
                        + band * math.tau / 3
                    )

                    py = (
                        center_y
                        + wave * beam_width * 0.25
                    )

                    points.append(
                        (int(px), int(py))
                    )

                pygame.draw.lines(
                    surface,
                    self.colors[band % len(self.colors)],
                    False,
                    points,
                    max(1, beam_width // 7),
                )

        pygame.draw.line(
            surface,
            self.highlight,
            (start_x, center_y),
            (end_x, center_y),
            max(2, beam_width // 2),
        )

        pygame.draw.line(
            surface,
            WHITE,
            (start_x, center_y),
            (end_x, center_y),
            max(1, beam_width // 5),
        )

        draw_glow(
            surface,
            self.x,
            self.y,
            beam_width + 8,
            self.highlight,
            int(120 * fade),
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (start_x, center_y),
            max(3, beam_width // 4),
        )

    def is_finished(self):
        return self.timer <= 0


# =====================================================
# PLAYER CLASS
# =====================================================

class Player:
    def __init__(self, x, y, is_fire):
        self.x = float(x)
        self.y = float(y)
        self.is_fire = is_fire

        self.hp = 100
        self.display_hp = 100
        self.speed = 5

        self.charging = False
        self.charge_time = 0
        self.charge_threshold = 45

        self.barrage_queue = 0
        self.barrage_cooldown = 0

        self.animation_time = random.random() * 10
        self.hit_flash = 0

        self.direction = 1 if is_fire else -1

        self.attack_timer = 0
        self.attack_duration = 18
        self.attack_flash = 0

        self.hand_pulse = random.random() * math.tau
        self.charge_pulse = random.random() * math.tau
        self.arm_sway = random.random() * math.tau
        self.energy_intensity = 0.0

        self.body_width = 28
        self.body_height = 44
        self.head_radius = 13

        self.color = (
            FIRE_MAIN if is_fire else WATER_MAIN
        )

        self.rect = pygame.Rect(
            int(x - 20),
            int(y - 45),
            40,
            75,
        )

    def move(self, up_key, down_key, keys):
        if keys[up_key]:
            self.y -= self.speed

        if keys[down_key]:
            self.y += self.speed

        self.y = max(
            125,
            min(GROUND_Y - 45, self.y),
        )

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def trigger_barrage(self):
        if self.barrage_cooldown <= 0 and self.barrage_queue == 0:
            self.barrage_queue = 5
            self.barrage_cooldown = 120

    def update(self, particles, projectiles):
        self.animation_time += 0.12
        self.hand_pulse += 0.16
        self.charge_pulse += 0.12
        self.arm_sway += 0.10

        self.display_hp += (
            self.hp - self.display_hp
        ) * 0.12

        if abs(self.hp - self.display_hp) < 0.1:
            self.display_hp = self.hp

        if self.hit_flash > 0:
            self.hit_flash -= 1

        if self.attack_timer > 0:
            self.attack_timer -= 1

        if self.attack_flash > 0:
            self.attack_flash -= 1

        if self.barrage_cooldown > 0:
            self.barrage_cooldown -= 1

        if self.barrage_queue > 0:
            if self.attack_timer <= 0:
                self.attack_timer = 6
                self.attack_flash = 5
                self.barrage_queue -= 1
                
                hand_x, hand_y = self.get_hand_position()
                spread_vy = random.uniform(-2.5, 2.5)
                
                projectiles.append(
                    Projectile(
                        hand_x,
                        hand_y,
                        self.direction,
                        self.is_fire,
                        charged=False,
                        vy=spread_vy,
                        radius=7,
                        damage=5,
                    )
                )

        target_intensity = 1.0 if self.charging else 0.0

        self.energy_intensity += (
            target_intensity - self.energy_intensity
        ) * 0.12

        if not self.charging:
            return

        self.charge_time += 1

        colors = (
            FIRE_COLORS if self.is_fire
            else WATER_COLORS
        )

        progress = min(
            1.0,
            self.charge_time / self.charge_threshold,
        )

        hand_x, hand_y = self.get_hand_position()
        angle = random.uniform(0, math.tau)

        if self.is_fire:
            radius = random.uniform(
                22,
                42 + progress * 18,
            )

            px = hand_x + math.cos(angle) * radius
            py = hand_y + math.sin(angle) * radius

            vx = (
                (hand_x - px) * 0.10
                + random.uniform(-1, 1)
            )

            vy = (
                (hand_y - py) * 0.10
                - random.uniform(0, 1.5)
            )

            size = random.randint(3, 7)
            lifetime = 18

        else:
            radius = random.uniform(
                25,
                38 + progress * 12,
            )

            orbit = angle + self.charge_time * 0.07

            px = hand_x + math.cos(orbit) * radius
            py = hand_y + math.sin(orbit) * radius

            vx = (
                (hand_x - px) * 0.065
                - math.sin(orbit) * 0.8
            )

            vy = (
                (hand_y - py) * 0.065
                + math.cos(orbit) * 0.8
            )

            size = random.randint(3, 6)
            lifetime = 22

        particles.append(
            Particle(
                px,
                py,
                random.choice(colors),
                size,
                lifetime,
                vx,
                vy,
            )
        )

        if progress >= 1.0 and random.random() < 0.45:
            particles.append(
                Particle(
                    hand_x + random.randint(-12, 12),
                    hand_y + random.randint(-12, 12),
                    WHITE if self.is_fire else colors[-1],
                    random.randint(3, 6),
                    12,
                    random.uniform(-1.5, 1.5),
                    random.uniform(-1.5, 1.5),
                )
            )

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        self.hit_flash = 8

    def get_hand_position(self):
        direction = self.direction

        shoulder_x = self.x + direction * 12
        shoulder_y = self.y - 14

        sway = math.sin(self.animation_time * 2.5) * 2
        pulse = math.sin(self.hand_pulse) * 1.5

        if self.charging:
            progress = min(
                1.0,
                self.charge_time / self.charge_threshold,
            )

            eased = progress * progress * (3 - 2 * progress)

            hand_x = shoulder_x - direction * (
                17 + eased * 18
            )

            hand_y = (
                shoulder_y + 15 + eased * 5 + sway
            )

        elif self.attack_timer > 0:
            progress = 1.0 - (
                self.attack_timer / self.attack_duration
            )

            if progress < 0.35:
                strike = progress / 0.35
                eased = 1 - (1 - strike) ** 3
            else:
                recovery = (progress - 0.35) / 0.65
                eased = 1.0 - recovery * 0.18

            hand_x = shoulder_x + direction * (
                24 + eased * 30
            )

            strike_progress = min(
                1.0,
                progress / 0.35,
            )

            hand_y = shoulder_y - 4 - math.sin(
                strike_progress * math.pi
            ) * 5

        else:
            hand_x = shoulder_x + direction * 18
            hand_y = shoulder_y + 14 + sway + pulse

        return hand_x, hand_y

    def release_attack(self):
        charged = (
            self.charge_time >= self.charge_threshold
        )

        self.charging = False
        self.charge_time = 0

        self.attack_timer = self.attack_duration
        self.attack_flash = 7

        if charged:
            return Beam(self)

        hand_x, hand_y = self.get_hand_position()

        return Projectile(
            hand_x,
            hand_y,
            self.direction,
            self.is_fire,
            False,
        )

    def draw(self, surface, target_x):
        self.direction = (
            1 if target_x > self.x else -1
        )

        direction = self.direction

        colors = (
            FIRE_COLORS if self.is_fire
            else WATER_COLORS
        )

        main_color = (
            FIRE_MAIN if self.is_fire
            else WATER_MAIN
        )

        highlight = colors[-1]
        t = self.animation_time

        breathe = math.sin(t * 2) * 2
        leg_swing = math.sin(t * 3) * 5

        head_y = self.y - 43 + breathe * 0.3
        shoulder_y = self.y - 14
        hip_y = self.y + 19
        head_x = self.x

        body_rect = pygame.Rect(
            int(self.x - 14),
            int(self.y - 27 + breathe * 0.3),
            28,
            44,
        )

        if self.charging:
            draw_glow(
                surface,
                self.x,
                self.y - 10,
                38,
                main_color,
                80,
            )

        left_hip = (self.x - 7, hip_y)
        right_hip = (self.x + 7, hip_y)

        left_foot = (
            self.x - 13 + leg_swing,
            self.y + 43,
        )

        right_foot = (
            self.x + 13 - leg_swing,
            self.y + 43,
        )

        left_knee = (self.x - 11 + leg_swing * 0.3, self.y + 28)
        right_knee = (self.x + 11 - leg_swing * 0.3, self.y + 28)

        pygame.draw.line(surface, BLACK, left_hip, left_knee, 11)
        pygame.draw.line(surface, main_color, left_hip, left_knee, 9)
        pygame.draw.line(surface, BLACK, left_knee, left_foot, 9)
        pygame.draw.line(surface, highlight, left_knee, left_foot, 7)

        pygame.draw.line(surface, BLACK, right_hip, right_knee, 11)
        pygame.draw.line(surface, main_color, right_hip, right_knee, 9)
        pygame.draw.line(surface, BLACK, right_knee, right_foot, 9)
        pygame.draw.line(surface, highlight, right_knee, right_foot, 7)

        pygame.draw.ellipse(surface, BLACK, (int(left_foot[0] - 9), int(left_foot[1] - 4), 18, 10))
        pygame.draw.ellipse(surface, main_color, (int(left_foot[0] - 8), int(left_foot[1] - 3), 16, 8))
        pygame.draw.ellipse(surface, BLACK, (int(right_foot[0] - 9), int(right_foot[1] - 4), 18, 10))
        pygame.draw.ellipse(surface, main_color, (int(right_foot[0] - 8), int(right_foot[1] - 3), 16, 8))

        back_shoulder = (
            self.x - direction * 12,
            shoulder_y,
        )

        back_elbow = (
            self.x - direction * 22,
            self.y + 1 + math.sin(t * 2) * 2,
        )

        back_hand = (
            self.x - direction * 24,
            self.y + 13,
        )

        pygame.draw.line(surface, BLACK, back_shoulder, back_elbow, 12)
        pygame.draw.line(surface, main_color, back_shoulder, back_elbow, 10)
        pygame.draw.line(surface, BLACK, back_elbow, back_hand, 10)
        pygame.draw.line(surface, highlight, back_elbow, back_hand, 8)
        pygame.draw.circle(surface, BLACK, (int(back_hand[0]), int(back_hand[1])), 8)
        pygame.draw.circle(surface, highlight, (int(back_hand[0]), int(back_hand[1])), 6)

        body_outline_rect = pygame.Rect(
            body_rect.x - 2,
            body_rect.y - 2,
            body_rect.width + 4,
            body_rect.height + 4,
        )
        pygame.draw.rect(surface, BLACK, body_outline_rect, border_radius=12)
        pygame.draw.rect(surface, main_color, body_rect, border_radius=10)

        pygame.draw.line(
            surface,
            highlight,
            (int(self.x), int(self.y - 22)),
            (int(self.x), int(self.y + 5)),
            4,
        )

        pygame.draw.circle(surface, BLACK, (int(self.x - 13), int(shoulder_y)), 9)
        pygame.draw.circle(surface, highlight, (int(self.x - 13), int(shoulder_y)), 7)

        pygame.draw.circle(surface, BLACK, (int(self.x + 13), int(shoulder_y)), 9)
        pygame.draw.circle(surface, highlight, (int(self.x + 13), int(shoulder_y)), 7)

        pygame.draw.circle(surface, BLACK, (int(head_x), int(head_y)), self.head_radius + 2)
        pygame.draw.circle(surface, main_color, (int(head_x), int(head_y)), self.head_radius)

        pygame.draw.circle(
            surface,
            highlight,
            (int(head_x), int(head_y - 2)),
            self.head_radius - 5,
        )

        eye_x = head_x + direction * 5

        pygame.draw.circle(
            surface,
            BLACK,
            (int(eye_x), int(head_y - 1)),
            3,
        )

        shoulder = (
            self.x + direction * 12,
            shoulder_y,
        )

        hand_x, hand_y = self.get_hand_position()

        if self.charging:
            progress = min(
                1.0,
                self.charge_time / self.charge_threshold,
            )

            elbow = (
                self.x - direction * (3 + progress * 4),
                self.y + 1 + progress * 2,
            )

        elif self.attack_timer > 0:
            progress = 1.0 - (
                self.attack_timer / self.attack_duration
            )

            elbow = (
                shoulder[0] + direction * (17 + progress * 9),
                shoulder[1] - 3 - math.sin(progress * math.pi) * 4,
            )

        else:
            elbow = (
                self.x + direction * 19,
                self.y + 1 + math.sin(self.arm_sway) * 2,
            )

        pygame.draw.line(
            surface,
            BLACK,
            (shoulder[0], shoulder[1] + 3),
            (elbow[0], elbow[1] + 3),
            13,
        )

        pygame.draw.line(
            surface,
            main_color,
            shoulder,
            elbow,
            11,
        )

        pygame.draw.line(
            surface,
            BLACK,
            (elbow[0], elbow[1]),
            (int(hand_x), int(hand_y)),
            10,
        )
        pygame.draw.line(
            surface,
            highlight,
            elbow,
            (int(hand_x), int(hand_y)),
            8,
        )

        charge_progress = min(
            1.0,
            self.charge_time / self.charge_threshold,
        ) if self.charging else 0.0

        pulse = (
            1 + math.sin(self.charge_pulse * 2) * 0.10
        )

        hand_radius = (
            int((9 + charge_progress * 8) * pulse)
            if self.charging else 9
        )

        if self.attack_flash > 0:
            hand_radius += self.attack_flash // 2

        if self.charging or self.attack_flash > 0:
            draw_glow(
                surface,
                hand_x,
                hand_y,
                hand_radius + 7,
                highlight,
                120,
            )

        if self.charging:
            if self.is_fire:
                for i in range(8):
                    angle = (
                        i * math.tau / 8
                        + self.charge_pulse * 0.7
                    )

                    inner = hand_radius + 2
                    outer = inner + random.randint(5, 11)

                    start = (
                        int(hand_x + math.cos(angle) * inner),
                        int(hand_y + math.sin(angle) * inner),
                    )

                    end = (
                        int(hand_x + math.cos(angle) * outer),
                        int(hand_y + math.sin(angle) * outer),
                    )

                    pygame.draw.line(
                        surface,
                        random.choice(colors),
                        start,
                        end,
                        2,
                    )

            else:
                for ring in range(2):
                    radius = hand_radius + 5 + ring * 7

                    pygame.draw.circle(
                        surface,
                        colors[(ring + 1) % len(colors)],
                        (int(hand_x), int(hand_y)),
                        radius,
                        2,
                    )

                for i in range(3):
                    angle = (
                        self.charge_pulse
                        + i * math.tau / 3
                    )

                    dx = math.cos(angle) * (hand_radius + 10)
                    dy = math.sin(angle) * (hand_radius + 10)

                    pygame.draw.circle(
                        surface,
                        highlight,
                        (int(hand_x + dx), int(hand_y + dy)),
                        3,
                    )

        pygame.draw.circle(
            surface,
            BLACK,
            (int(hand_x), int(hand_y)),
            hand_radius + 1,
        )
        pygame.draw.circle(
            surface,
            highlight,
            (int(hand_x), int(hand_y)),
            hand_radius,
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (int(hand_x), int(hand_y)),
            max(2, hand_radius // 3),
        )

        if self.charging and charge_progress >= 1:
            ring_radius = int(
                24 + math.sin(self.charge_pulse * 2) * 3
            )

            pygame.draw.circle(
                surface,
                WHITE,
                (int(hand_x), int(hand_y)),
                ring_radius,
                2,
            )

        if self.attack_flash > 0:
            pygame.draw.circle(
                surface,
                WHITE,
                (int(hand_x), int(hand_y)),
                12 + self.attack_flash * 2,
                2,
            )


# =====================================================
# HEALTH BARS
# =====================================================

def draw_health_bar(surface, x, y, player, label):
    width = 380
    height = 22

    pygame.draw.rect(
        surface,
        (55, 35, 50),
        (x, y, width, height),
        border_radius=6,
    )

    health_width = int(
        width * max(0, player.display_hp) / 100
    )

    health_color = (
        FIRE_MAIN if player.is_fire else WATER_MAIN
    )

    if health_width > 0:
        pygame.draw.rect(
            surface,
            health_color,
            (x, y, health_width, height),
            border_radius=6,
        )

    pygame.draw.rect(
        surface,
        WHITE,
        (x, y, width, height),
        2,
        border_radius=6,
    )

    text = FONT.render(
        f"{label}: {player.hp} HP",
        True,
        WHITE,
    )

    surface.blit(text, (x, y - 29))


# =====================================================
# INITIALIZE GAME
# =====================================================

fire = Player(180, 400, True)
water = Player(920, 400, False)

players = [fire, water]

projectiles = []
beams = []
particles = []

game_over = False
winner_text = ""

charging_keys = {
    pygame.K_f: fire,
    pygame.K_RETURN: water,
}

barrage_keys = {
    pygame.K_g: fire,
    pygame.K_RSHIFT: water,
}

moving_keys = {
    fire: (pygame.K_w, pygame.K_s),
    water: (pygame.K_UP, pygame.K_DOWN),
}

background_time = 0.0
running = True


# =====================================================
# MAIN GAME LOOP
# =====================================================

while running:
    clock.tick(FPS)
    background_time += 0.025

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if not game_over:
                if event.key in charging_keys:
                    player = charging_keys[event.key]

                    if player.hp > 0 and not player.charging:
                        player.charging = True
                        player.charge_time = 0

                if event.key in barrage_keys:
                    player = barrage_keys[event.key]
                    if player.hp > 0:
                        player.trigger_barrage()

            if game_over and event.key == pygame.K_r:
                fire = Player(180, 400, True)
                water = Player(920, 400, False)

                players = [fire, water]

                projectiles.clear()
                beams.clear()
                particles.clear()

                game_over = False
                winner_text = ""

                moving_keys = {
                    fire: (pygame.K_w, pygame.K_s),
                    water: (pygame.K_UP, pygame.K_DOWN),
                }

                charging_keys = {
                    pygame.K_f: fire,
                    pygame.K_RETURN: water,
                }

                barrage_keys = {
                    pygame.K_g: fire,
                    pygame.K_RSHIFT: water,
                }

        if event.type == pygame.KEYUP:
            if event.key in charging_keys:
                player = charging_keys[event.key]

                if player.charging:
                    attack = player.release_attack()

                    if isinstance(attack, Beam):
                        beams.append(attack)
                    else:
                        projectiles.append(attack)

    keys = pygame.key.get_pressed()

    if not game_over:
        for player in players:
            if player.hp > 0:
                up_key, down_key = moving_keys[player]

                player.move(up_key, down_key, keys)

            player.update(particles, projectiles)

        for projectile in projectiles[:]:
            projectile.update(particles)

            if projectile.is_finished():
                projectiles.remove(projectile)
                continue

            target = (
                water if projectile.is_fire else fire
            )

            if (
                target.hp > 0
                and projectile.rect.colliderect(target.rect)
            ):
                target.take_damage(projectile.damage)

                impact_colors = (
                    FIRE_COLORS if projectile.is_fire
                    else WATER_COLORS
                )

                for _ in range(12):
                    particles.append(
                        Particle(
                            projectile.x,
                            projectile.y,
                            random.choice(impact_colors),
                            random.randint(3, 7),
                            15,
                            random.uniform(-4, 4),
                            random.uniform(-4, 4),
                        )
                    )

                projectiles.remove(projectile)

        for beam in beams[:]:
            beam.update(particles)

            if beam.is_finished():
                beams.remove(beam)
                continue

            target = (
                water if beam.is_fire else fire
            )

            if target.hp > 0 and beam.timer == beam.max_timer - 1:
                if beam.rect.colliderect(target.rect):
                    target.take_damage(beam.damage)

                    impact_colors = (
                        FIRE_COLORS if beam.is_fire
                        else WATER_COLORS
                    )

                    for _ in range(25):
                        particles.append(
                            Particle(
                                target.x,
                                target.y + random.uniform(-20, 20),
                                random.choice(impact_colors),
                                random.randint(4, 9),
                                20,
                                beam.direction * random.uniform(2, 6),
                                random.uniform(-3, 3),
                            )
                        )

        for particle in particles[:]:
            particle.update()

            if particle.is_dead():
                particles.remove(particle)

        if fire.hp <= 0 or water.hp <= 0:
            game_over = True

            if fire.hp <= 0 and water.hp <= 0:
                winner_text = "IT'S A DRAW!"
            elif fire.hp <= 0:
                winner_text = "WATER WINS!"
            else:
                winner_text = "FIRE WINS!"

    draw_background(screen, background_time)

    for particle in particles:
        particle.draw(screen)

    for projectile in projectiles:
        projectile.draw(screen)

    for beam in beams:
        beam.draw(screen)

    fire.draw(screen, water.x)
    water.draw(screen, fire.x)

    draw_health_bar(screen, 60, 35, fire, "Fire")
    draw_health_bar(screen, WIDTH - 440, 35, water, "Water")

    if game_over:
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )
        overlay.fill((10, 14, 25, 180))
        screen.blit(overlay, (0, 0))

        win_text = FONT.render(winner_text, True, WHITE)
        restart_text = SMALL_FONT.render(
            "Press 'R' to Restart or 'ESC' to Quit",
            True,
            (170, 185, 215),
        )

        screen.blit(
            win_text,
            (
                WIDTH // 2 - win_text.get_width() // 2,
                HEIGHT // 2 - 35,
            ),
        )
        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                HEIGHT // 2 + 10,
            ),
        )

    pygame.display.flip()

pygame.quit()
