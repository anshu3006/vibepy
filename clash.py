import pygame
import math
import random
import sys

# =========================================================
# INITIALIZATION
# =========================================================

pygame.init()

WIDTH, HEIGHT = 1000, 650
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ELEMENTAL CLASH: FIRE VS WATER")

clock = pygame.time.Clock()

# Fonts
FONT_SMALL = pygame.font.SysFont("consolas", 16, bold=True)
FONT_MEDIUM = pygame.font.SysFont("consolas", 24, bold=True)
FONT_LARGE = pygame.font.SysFont("consolas", 48, bold=True)
FONT_TITLE = pygame.font.SysFont("consolas", 64, bold=True)

# Colors
BLACK = (5, 7, 18)
WHITE = (255, 255, 255)

FIRE_COLORS = [
    (255, 35, 10),
    (255, 90, 0),
    (255, 160, 0),
    (255, 230, 80),
]

WATER_COLORS = [
    (0, 80, 255),
    (0, 160, 255),
    (0, 220, 255),
    (150, 245, 255),
]

FIRE_MAIN = (255, 55, 15)
WATER_MAIN = (0, 150, 255)

GROUND_Y = HEIGHT - 65

# =========================================================
# BACKGROUND
# =========================================================

def create_background():
    """Create a static gradient background."""

    bg = pygame.Surface((WIDTH, HEIGHT))

    top_color = (8, 8, 30)
    bottom_color = (35, 12, 40)

    for y in range(HEIGHT):
        t = y / HEIGHT

        color = (
            int(top_color[0] * (1 - t) + bottom_color[0] * t),
            int(top_color[1] * (1 - t) + bottom_color[1] * t),
            int(top_color[2] * (1 - t) + bottom_color[2] * t),
        )

        pygame.draw.line(bg, color, (0, y), (WIDTH, y))

    # Distant mountains
    pygame.draw.polygon(
        bg,
        (17, 19, 45),
        [
            (0, 380),
            (120, 250),
            (220, 350),
            (360, 220),
            (490, 365),
            (650, 245),
            (790, 355),
            (920, 230),
            (WIDTH, 330),
            (WIDTH, HEIGHT),
            (0, HEIGHT),
        ],
    )

    # Farther mountain silhouettes
    pygame.draw.polygon(
        bg,
        (24, 22, 53),
        [
            (0, 430),
            (180, 330),
            (300, 410),
            (470, 300),
            (620, 420),
            (790, 320),
            (WIDTH, 415),
            (WIDTH, HEIGHT),
            (0, HEIGHT),
        ],
    )

    # Ground
    pygame.draw.rect(
        bg,
        (12, 15, 32),
        (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y),
    )

    # Ground lines
    pygame.draw.line(
        bg,
        (80, 55, 100),
        (0, GROUND_Y),
        (WIDTH, GROUND_Y),
        2,
    )

    for x in range(-WIDTH, WIDTH * 2, 100):
        pygame.draw.line(
            bg,
            (30, 30, 60),
            (WIDTH // 2, GROUND_Y),
            (x, HEIGHT),
            1,
        )

    for y in range(GROUND_Y + 20, HEIGHT, 20):
        pygame.draw.line(
            bg,
            (25, 27, 50),
            (0, y),
            (WIDTH, y),
            1,
        )

    # Background decorations
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(60, GROUND_Y - 30)
        radius = random.choice([1, 1, 2])

        pygame.draw.circle(
            bg,
            (60, 65, 100),
            (x, y),
            radius,
        )

    return bg


background = create_background()


# =========================================================
# PARTICLES
# =========================================================

class Particle:
    def __init__(
        self,
        x,
        y,
        color,
        size,
        life,
        speed_x,
        speed_y,
        gravity=0,
    ):
        self.x = float(x)
        self.y = float(y)

        self.color = color
        self.size = float(size)

        self.life = life
        self.max_life = life

        self.speed_x = speed_x
        self.speed_y = speed_y

        self.gravity = gravity

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        self.speed_y += self.gravity

        self.life -= 1

        self.size *= 0.97

    def draw(self, surface):
        if self.life <= 0 or self.size <= 0:
            return

        alpha = int(
            255 * max(0, self.life / self.max_life)
        )

        radius = max(1, int(self.size))

        particle_surface = pygame.Surface(
            (radius * 4, radius * 4),
            pygame.SRCALPHA,
        )

        center = (radius * 2, radius * 2)

        # Outer glow
        pygame.draw.circle(
            particle_surface,
            (*self.color, alpha // 4),
            center,
            radius * 2,
        )

        # Main particle
        pygame.draw.circle(
            particle_surface,
            (*self.color, alpha),
            center,
            radius,
        )

        surface.blit(
            particle_surface,
            (
                int(self.x - radius * 2),
                int(self.y - radius * 2),
            ),
        )


# =========================================================
# GLOW EFFECT
# =========================================================

def draw_glow(surface, x, y, radius, color, intensity=150):
    """Draw a soft circular glow."""

    radius = max(1, int(radius))

    glow_surface = pygame.Surface(
        (radius * 4, radius * 4),
        pygame.SRCALPHA,
    )

    center = (radius * 2, radius * 2)

    pygame.draw.circle(
        glow_surface,
        (*color, max(0, min(255, intensity // 5))),
        center,
        radius * 2,
    )

    pygame.draw.circle(
        glow_surface,
        (*color, max(0, min(255, intensity // 3))),
        center,
        int(radius * 1.5),
    )

    pygame.draw.circle(
        glow_surface,
        (*color, max(0, min(255, intensity))),
        center,
        radius,
    )

    surface.blit(
        glow_surface,
        (int(x - radius * 2), int(y - radius * 2)),
        special_flags=pygame.BLEND_RGBA_ADD,
    )


# =========================================================
# ANIMATED BACKGROUND PARTICLES
# =========================================================

class BackgroundParticle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(70, GROUND_Y)

        self.speed_y = random.uniform(-0.8, -0.15)
        self.speed_x = random.uniform(-0.3, 0.3)

        self.size = random.randint(1, 3)

        self.color = random.choice(
            FIRE_COLORS + WATER_COLORS
        )

        self.alpha = random.randint(60, 180)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.y < 60:
            self.reset()
            self.y = GROUND_Y

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            self.size,
        )


background_particles = [
    BackgroundParticle() for _ in range(45)
]


# =========================================================
# PLAYER
# =========================================================

class Player:
    def __init__(self, x, y, is_fire):
        self.x = float(x)
        self.y = float(y)

        self.is_fire = is_fire

        self.hp = 100
        self.display_hp = 100

        self.speed = 5

        self.radius = 25

        self.charging = False
        self.charge_time = 0
        self.charge_threshold = 45

        self.animation_time = random.random() * 10

        self.hit_flash = 0

        self.rect = pygame.Rect(
            int(x - self.radius),
            int(y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

        self.color = FIRE_MAIN if is_fire else WATER_MAIN

        self.particles = []

    def move(self, up_key, down_key, keys):
        if keys[up_key]:
            self.y -= self.speed

        if keys[down_key]:
            self.y += self.speed

        self.y = max(
            100,
            min(GROUND_Y - self.radius, self.y),
        )

        self.rect.center = (
            int(self.x),
            int(self.y),
        )

    def update(self, particles):
        self.animation_time += 0.12

        # Smooth HP animation
        self.display_hp += (
            self.hp - self.display_hp
        ) * 0.12

        if abs(self.hp - self.display_hp) < 0.1:
            self.display_hp = self.hp

        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Generate charging energy
        if self.charging:
            self.charge_time += 1

            colors = (
                FIRE_COLORS if self.is_fire
                else WATER_COLORS
            )

            angle = random.uniform(0, math.tau)

            radius = random.randint(
                25,
                min(65, 28 + self.charge_time),
            )

            px = self.x + math.cos(angle) * radius
            py = self.y + math.sin(angle) * radius

            particles.append(
                Particle(
                    px,
                    py,
                    random.choice(colors),
                    random.randint(3, 7),
                    18,
                    (self.x - px) * 0.08,
                    (self.y - py) * 0.08,
                )
            )

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        self.hit_flash = 8

    def release_attack(self):
        charged = (
            self.charge_time >= self.charge_threshold
        )

        direction = 1 if self.is_fire else -1

        projectile = Projectile(
            self.x + direction * 35,
            self.y,
            direction,
            self.is_fire,
            charged,
        )

        self.charging = False
        self.charge_time = 0

        return projectile

    def draw(self, surface):
        pulse = math.sin(self.animation_time * 2)

        # Body colors
        colors = (
            FIRE_COLORS if self.is_fire
            else WATER_COLORS
        )

        core_color = (
            (255, 240, 200)
            if self.is_fire
            else (220, 250, 255)
        )

        # Character glow
        draw_glow(
            surface,
            self.x,
            self.y,
            35 + pulse * 3,
            self.color,
            110,
        )

        # Orbiting energy particles
        for i in range(4):
            angle = (
                self.animation_time
                + i * math.pi / 2
            )

            orbit_radius = 34 + pulse * 3

            px = self.x + math.cos(angle) * orbit_radius
            py = self.y + math.sin(angle) * orbit_radius

            pygame.draw.circle(
                surface,
                colors[i % len(colors)],
                (int(px), int(py)),
                4,
            )

        # Fire flames or water droplets
        for i in range(7):
            angle = (
                self.animation_time * 1.5
                + i * math.tau / 7
            )

            distance = (
                26
                + math.sin(
                    self.animation_time * 3 + i
                ) * 5
            )

            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance

            size = random.randint(5, 8)

            if self.is_fire:
                points = [
                    (int(px), int(py - size)),
                    (int(px - size * 0.7), int(py + size)),
                    (int(px + size * 0.7), int(py + size)),
                ]

                pygame.draw.polygon(
                    surface,
                    random.choice(colors),
                    points,
                )

            else:
                pygame.draw.circle(
                    surface,
                    random.choice(colors),
                    (int(px), int(py)),
                    size // 2,
                )

        # Main character core
        if self.hit_flash > 0:
            body_color = WHITE
        else:
            body_color = self.color

        pygame.draw.circle(
            surface,
            body_color,
            (int(self.x), int(self.y)),
            self.radius,
        )

        # Inner energy core
        pygame.draw.circle(
            surface,
            core_color,
            (int(self.x), int(self.y)),
            13,
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (int(self.x), int(self.y)),
            6,
        )

        # Charged attack aura
        if self.charging:
            charge_progress = min(
                1,
                self.charge_time / self.charge_threshold,
            )

            aura_radius = int(
                30 + charge_progress * 18
            )

            pygame.draw.circle(
                surface,
                colors[-1],
                (int(self.x), int(self.y)),
                aura_radius,
                2,
            )

            if charge_progress >= 1:
                pygame.draw.circle(
                    surface,
                    WHITE,
                    (int(self.x), int(self.y)),
                    aura_radius + 5,
                    2,
                )


# =========================================================
# PROJECTILES
# =========================================================

class Projectile:
    def __init__(
        self,
        x,
        y,
        direction,
        is_fire,
        is_charged,
    ):
        self.x = float(x)
        self.y = float(y)

        self.direction = direction
        self.is_fire = is_fire
        self.is_charged = is_charged

        self.active = True

        self.animation_time = 0

        if is_charged:
            self.speed = 8
            self.width = 46
            self.height = 180
            self.damage = 30
        else:
            self.speed = 15
            self.width = 25
            self.height = 25
            self.damage = 10

        self.rect = pygame.Rect(
            int(x - self.width // 2),
            int(y - self.height // 2),
            self.width,
            self.height,
        )

    def update(self, particles):
        self.animation_time += 0.2

        self.x += self.speed * self.direction

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        colors = (
            FIRE_COLORS if self.is_fire
            else WATER_COLORS
        )

        # Charged projectile particles
        if self.is_charged:
            for _ in range(6):
                offset_y = random.randint(
                    -self.height // 2,
                    self.height // 2,
                )

                particles.append(
                    Particle(
                        self.x + random.randint(-20, 20),
                        self.y + offset_y,
                        random.choice(colors),
                        random.randint(4, 10),
                        random.randint(12, 25),
                        random.uniform(-1, 1),
                        random.uniform(-2, 2),
                    )
                )

        else:
            # Normal projectile trail
            for _ in range(3):
                particles.append(
                    Particle(
                        self.x - self.direction * 8,
                        self.y + random.randint(-8, 8),
                        random.choice(colors),
                        random.randint(4, 9),
                        random.randint(10, 20),
                        random.uniform(-2, 0)
                        * self.direction,
                        random.uniform(-1.5, 1.5),
                    )
                )

        if self.x < -100 or self.x > WIDTH + 100:
            self.active = False

    def draw(self, surface):
        colors = (
            FIRE_COLORS if self.is_fire
            else WATER_COLORS
        )

        # Large charged attack
        if self.is_charged:
            glow_color = colors[1]

            beam_rect = pygame.Rect(
                int(self.x - self.width // 2),
                int(self.y - self.height // 2),
                self.width,
                self.height,
            )

            glow_surface = pygame.Surface(
                (self.width + 50, self.height + 20),
                pygame.SRCALPHA,
            )

            pygame.draw.ellipse(
                glow_surface,
                (*glow_color, 55),
                glow_surface.get_rect(),
            )

            surface.blit(
                glow_surface,
                (
                    int(self.x - glow_surface.get_width() / 2),
                    int(self.y - self.height / 2 - 10),
                ),
                special_flags=pygame.BLEND_RGBA_ADD,
            )

            pygame.draw.rect(
                surface,
                colors[0],
                beam_rect,
                border_radius=20,
            )

            inner_rect = beam_rect.inflate(-18, -10)

            pygame.draw.rect(
                surface,
                colors[-1],
                inner_rect,
                border_radius=15,
            )

            # Energy streaks
            for i in range(5):
                offset_x = math.sin(
                    self.animation_time + i
                ) * 12

                pygame.draw.line(
                    surface,
                    WHITE,
                    (
                        int(self.x + offset_x),
                        int(self.y - self.height // 2),
                    ),
                    (
                        int(self.x - offset_x),
                        int(self.y + self.height // 2),
                    ),
                    2,
                )

        else:
            # Normal glowing projectile
            draw_glow(
                surface,
                self.x,
                self.y,
                18,
                colors[1],
                130,
            )

            # Main projectile
            pygame.draw.circle(
                surface,
                colors[0],
                (int(self.x), int(self.y)),
                12,
            )

            pygame.draw.circle(
                surface,
                colors[-1],
                (int(self.x), int(self.y)),
                7,
            )

            pygame.draw.circle(
                surface,
                WHITE,
                (int(self.x), int(self.y)),
                3,
            )


# =========================================================
# HEALTH BARS AT THE TOP
# =========================================================

def draw_health_bars(surface, player1, player2):
    bar_width = 360
    bar_height = 22
    bar_y = 28

    left_x = 35
    right_x = WIDTH - 35 - bar_width

    # Player names
    fire_text = FONT_MEDIUM.render(
        "FIRE",
        True,
        FIRE_COLORS[2],
    )

    water_text = FONT_MEDIUM.render(
        "WATER",
        True,
        WATER_COLORS[2],
    )

    surface.blit(fire_text, (left_x, 3))

    surface.blit(
        water_text,
        (
            right_x + bar_width - water_text.get_width(),
            3,
        ),
    )

    # Background bars
    pygame.draw.rect(
        surface,
        (45, 35, 55),
        (left_x, bar_y, bar_width, bar_height),
        border_radius=8,
    )

    pygame.draw.rect(
        surface,
        (45, 35, 55),
        (right_x, bar_y, bar_width, bar_height),
        border_radius=8,
    )

    # Health proportions
    fire_ratio = max(
        0,
        min(1, player1.display_hp / 100),
    )

    water_ratio = max(
        0,
        min(1, player2.display_hp / 100),
    )

    fire_width = int(bar_width * fire_ratio)
    water_width = int(bar_width * water_ratio)

    # Fire health bar
    if fire_width > 0:
        pygame.draw.rect(
            surface,
            FIRE_COLORS[0],
            (
                left_x,
                bar_y,
                fire_width,
                bar_height,
            ),
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            FIRE_COLORS[2],
            (
                left_x,
                bar_y,
                fire_width,
                5,
            ),
            border_radius=5,
        )

    # Water health bar grows from the right
    if water_width > 0:
        pygame.draw.rect(
            surface,
            WATER_COLORS[0],
            (
                right_x + bar_width - water_width,
                bar_y,
                water_width,
                bar_height,
            ),
            border_radius=8,
        )

        pygame.draw.rect(
            surface,
            WATER_COLORS[2],
            (
                right_x + bar_width - water_width,
                bar_y,
                water_width,
                5,
            ),
            border_radius=5,
        )

    # Bar borders
    pygame.draw.rect(
        surface,
        (150, 80, 80),
        (left_x, bar_y, bar_width, bar_height),
        2,
        border_radius=8,
    )

    pygame.draw.rect(
        surface,
        (60, 130, 200),
        (right_x, bar_y, bar_width, bar_height),
        2,
        border_radius=8,
    )

    # HP numbers
    fire_hp_text = FONT_SMALL.render(
        f"{player1.hp} / 100",
        True,
        WHITE,
    )

    water_hp_text = FONT_SMALL.render(
        f"{player2.hp} / 100",
        True,
        WHITE,
    )

    surface.blit(
        fire_hp_text,
        (
            left_x + bar_width // 2
            - fire_hp_text.get_width() // 2,
            bar_y + 3,
        ),
    )

    surface.blit(
        water_hp_text,
        (
            right_x + bar_width // 2
            - water_hp_text.get_width() // 2,
            bar_y + 3,
        ),
    )


# =========================================================
# CHARGE INDICATOR
# =========================================================

def draw_charge_indicator(surface, player, x, y):
    if not player.charging:
        return

    progress = min(
        1,
        player.charge_time / player.charge_threshold,
    )

    bar_width = 120
    bar_height = 8

    pygame.draw.rect(
        surface,
        (45, 45, 60),
        (x, y, bar_width, bar_height),
        border_radius=4,
    )

    colors = (
        FIRE_COLORS if player.is_fire
        else WATER_COLORS
    )

    pygame.draw.rect(
        surface,
        colors[2],
        (
            x,
            y,
            int(bar_width * progress),
            bar_height,
        ),
        border_radius=4,
    )

    if progress >= 1:
        label = FONT_SMALL.render(
            "POWER READY!",
            True,
            WHITE,
        )

        surface.blit(
            label,
            (x, y - 22),
        )


# =========================================================
# EXPLOSION EFFECT
# =========================================================

def create_explosion(x, y, particles, is_fire, charged=False):
    colors = (
        FIRE_COLORS if is_fire
        else WATER_COLORS
    )

    count = 45 if charged else 22

    for _ in range(count):
        angle = random.uniform(0, math.tau)

        speed = random.uniform(
            2,
            8 if charged else 5,
        )

        particles.append(
            Particle(
                x,
                y,
                random.choice(colors),
                random.randint(4, 12),
                random.randint(15, 35),
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                gravity=0.03 if is_fire else 0,
            )
        )


# =========================================================
# VICTORY SCREEN
# =========================================================

def draw_victory_screen(surface, winner, elapsed):
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA,
    )

    overlay.fill((0, 0, 0, 190))

    surface.blit(overlay, (0, 0))

    if winner == "FIRE":
        color = FIRE_COLORS[2]
    else:
        color = WATER_COLORS[2]

    title = FONT_TITLE.render(
        winner + " WINS!",
        True,
        color,
    )

    shadow = FONT_TITLE.render(
        winner + " WINS!",
        True,
        (70, 40, 70),
    )

    title_x = WIDTH // 2 - title.get_width() // 2
    title_y = HEIGHT // 2 - 80

    surface.blit(
        shadow,
        (title_x + 4, title_y + 4),
    )

    surface.blit(
        title,
        (title_x, title_y),
    )

    subtitle = FONT_MEDIUM.render(
        "ELEMENTAL CLASH",
        True,
        WHITE,
    )

    surface.blit(
        subtitle,
        (
            WIDTH // 2 - subtitle.get_width() // 2,
            HEIGHT // 2,
        ),
    )

    restart = FONT_SMALL.render(
        "PRESS R TO RESTART  |  ESC TO QUIT",
        True,
        (200, 200, 220),
    )

    surface.blit(
        restart,
        (
            WIDTH // 2 - restart.get_width() // 2,
            HEIGHT // 2 + 60,
        ),
    )


# =========================================================
# MAIN GAME
# =========================================================

def main():
    player1 = Player(
        110,
        HEIGHT // 2,
        is_fire=True,
    )

    player2 = Player(
        WIDTH - 110,
        HEIGHT // 2,
        is_fire=False,
    )

    particles = []
    projectiles = []

    running = True
    game_over = False
    winner = None

    screen_shake = 0

    while running:
        clock.tick(FPS)

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if not game_over:
                    if (
                        event.key == pygame.K_SPACE
                        and not player1.charging
                    ):
                        player1.charging = True
                        player1.charge_time = 0

                    if (
                        event.key == pygame.K_RETURN
                        and not player2.charging
                    ):
                        player2.charging = True
                        player2.charge_time = 0

                elif event.key == pygame.K_r:
                    main()
                    return

            if event.type == pygame.KEYUP:
                if not game_over:
                    if (
                        event.key == pygame.K_SPACE
                        and player1.charging
                    ):
                        projectiles.append(
                            player1.release_attack()
                        )

                    if (
                        event.key == pygame.K_RETURN
                        and player2.charging
                    ):
                        projectiles.append(
                            player2.release_attack()
                        )

        keys = pygame.key.get_pressed()

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        if not game_over:
            player1.move(
                pygame.K_w,
                pygame.K_s,
                keys,
            )

            player2.move(
                pygame.K_UP,
                pygame.K_DOWN,
                keys,
            )

            player1.update(particles)
            player2.update(particles)

            # Update background
            for particle in background_particles:
                particle.update()

            # Update projectiles
            for proj in projectiles[:]:
                proj.update(particles)

                target = (
                    player2 if proj.is_fire
                    else player1
                )

                if proj.rect.colliderect(target.rect):
                    target.take_damage(proj.damage)

                    create_explosion(
                        proj.x,
                        proj.y,
                        particles,
                        proj.is_fire,
                        proj.is_charged,
                    )

                    proj.active = False

                    screen_shake = (
                        12 if proj.is_charged else 5
                    )

                if not proj.active:
                    if proj in projectiles:
                        projectiles.remove(proj)

            # Update particles
            for particle in particles[:]:
                particle.update()

                if particle.life <= 0:
                    particles.remove(particle)

            # Keep particle count under control
            if len(particles) > 1200:
                particles = particles[-1000:]

            # Screen shake
            if screen_shake > 0:
                screen_shake -= 1

            # Victory check
            if player1.hp <= 0:
                game_over = True
                winner = "WATER"

            elif player2.hp <= 0:
                game_over = True
                winner = "FIRE"

        else:
            # Continue animating particles after victory
            for particle in particles[:]:
                particle.update()

                if particle.life <= 0:
                    particles.remove(particle)

        # -------------------------------------------------
        # DRAW BACKGROUND
        # -------------------------------------------------

        screen.fill(BLACK)

        shake_x = 0
        shake_y = 0

        if screen_shake > 0:
            shake_x = random.randint(
                -screen_shake // 2,
                screen_shake // 2,
            )

            shake_y = random.randint(
                -screen_shake // 2,
                screen_shake // 2,
            )

        # Draw the background with screen shake
        screen.blit(
            background,
            (shake_x, shake_y),
        )

        # Draw ambient particles
        for particle in background_particles:
            particle.draw(screen)

        # -------------------------------------------------
        # DRAW PROJECTILES
        # -------------------------------------------------

        for proj in projectiles:
            proj.draw(screen)

        # -------------------------------------------------
        # DRAW PARTICLES
        # -------------------------------------------------

        for particle in particles:
            particle.draw(screen)

        # -------------------------------------------------
        # DRAW PLAYERS
        # -------------------------------------------------

        player1.draw(screen)
        player2.draw(screen)

        # -------------------------------------------------
        # DRAW UI
        # -------------------------------------------------

        draw_health_bars(
            screen,
            player1,
            player2,
        )

        draw_charge_indicator(
            screen,
            player1,
            35,
            65,
        )

        draw_charge_indicator(
            screen,
            player2,
            WIDTH - 155,
            65,
        )

        # Center divider
        pygame.draw.line(
            screen,
            (65, 55, 100),
            (WIDTH // 2, 85),
            (WIDTH // 2, GROUND_Y),
            1,
        )

        # Control hints
        controls = FONT_SMALL.render(
            "FIRE: W/S + SPACE"
            "        WATER: UP/DOWN + ENTER",
            True,
            (155, 160, 190),
        )

        screen.blit(
            controls,
            (
                WIDTH // 2 - controls.get_width() // 2,
                HEIGHT - 35,
            ),
        )

        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------

        if game_over:
            draw_victory_screen(
                screen,
                winner,
                pygame.time.get_ticks() / 1000,
            )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
