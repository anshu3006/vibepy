import math
import random
import sys
import pygame

pygame.init()

# =====================================================
# GAME SETTINGS & CONSTANTS
# =====================================================

WIDTH, HEIGHT = 1100, 650
GROUND_Y = 540
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elemental Clash - Shield Cooldown Edition")
clock = pygame.time.Clock()

# Battle scenes are drawn to this offscreen surface first so a screen shake
# can nudge the whole picture without touching game logic or UI math.
game_surface = pygame.Surface((WIDTH, HEIGHT))

WHITE = (245, 250, 255)
BLACK = (15, 18, 30)
BG = (12, 16, 35)
GROUND = (28, 35, 57)

ELEMENT_DATA = {
    'fire': {
        'name': 'FIRE',
        'main': (235, 55, 25),
        'colors': [(255, 70, 20), (255, 135, 25), (255, 205, 55), (255, 245, 190)],
        'p1_controls': 'P1: WASD Move | E Shield | Hold F (Beam) | G (Burst)',
        'p2_controls': 'P2: ARROWS Move | RCTRL Shield | Hold ENTER (Beam) | RSHIFT (Burst)',
    },
    'water': {
        'name': 'WATER',
        'main': (25, 105, 230),
        'colors': [(20, 80, 230), (25, 170, 255), (100, 225, 255), (220, 250, 255)],
        'p1_controls': 'P1: WASD Move | E Shield | Hold F (Beam) | G (Burst)',
        'p2_controls': 'P2: ARROWS Move | RCTRL Shield | Hold ENTER (Beam) | RSHIFT (Burst)',
    },
    'earth': {
        'name': 'EARTH',
        'main': (45, 165, 60),
        'colors': [(30, 110, 40), (60, 190, 75), (135, 225, 100), (210, 245, 170)],
        'p1_controls': 'P1: WASD Move | E Shield | Hold F (Vines) | G (Bullet Seeds)',
        'p2_controls': 'P2: ARROWS Move | RCTRL Shield | Hold ENTER (Vines) | RSHIFT (Bullet Seeds)',
    }
}

TITLE_FONT = pygame.font.SysFont("arial", 42, bold=True)
FONT = pygame.font.SysFont("arial", 20, bold=True)
LARGE_FONT = pygame.font.SysFont("arial", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 13, bold=True)


# =====================================================
# TYPE EFFECTIVENESS
# =====================================================

def get_type_multiplier(attacker_type, defender_type):
    if (attacker_type == 'water' and defender_type == 'fire') or \
       (attacker_type == 'fire' and defender_type == 'earth') or \
       (attacker_type == 'earth' and defender_type == 'water'):
        return 1.5
    return 1.0


# =====================================================
# VISUAL HELPERS
# =====================================================

def draw_glow(surface, x, y, radius, color, alpha=100):
    radius = max(1, int(radius))
    glow = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
    cx = cy = radius * 3

    for i in range(5, 0, -1):
        r = max(1, int(radius * i * 0.6))
        a = max(1, int(alpha / (i * 1.5)))
        pygame.draw.circle(glow, (*color, min(255, a)), (cx, cy), r)

    surface.blit(glow, (int(x - cx), int(y - cy)), special_flags=pygame.BLEND_RGBA_ADD)


def draw_honeycomb_shield(surface, x, y, radius):
    shield_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
    cx, cy = radius + 5, radius + 5

    pygame.draw.circle(shield_surf, (200, 230, 255, 90), (cx, cy), radius, 3)

    hex_size = 11
    h_width = math.sqrt(3) * hex_size
    h_height = 2 * hex_size

    for row in range(-3, 4):
        for col in range(-3, 4):
            hx = cx + col * h_width + (row % 2) * (h_width / 2)
            hy = cy + row * (h_height * 0.75)

            if math.hypot(hx - cx, hy - cy) < radius - 4:
                is_light = (row + col) % 2 == 0
                color = (235, 245, 255, 120) if is_light else (110, 150, 195, 85)

                points = []
                for i in range(6):
                    angle = math.tau / 6 * i + math.pi / 6
                    points.append((hx + hex_size * 0.8 * math.cos(angle), hy + hex_size * 0.8 * math.sin(angle)))
                
                pygame.draw.polygon(shield_surf, color, points)
                pygame.draw.polygon(shield_surf, (255, 255, 255, 160), points, 1)

    surface.blit(shield_surf, (int(x - cx), int(y - cy)))


def draw_background(surface, t):
    surface.fill(BG)

    for i in range(12):
        x = i * (WIDTH // 11)
        y = 100 + math.sin(t + i * 0.8) * 25
        pygame.draw.circle(surface, (20, 30, 65), (int(x), int(y)), 55)

    pygame.draw.rect(surface, GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.line(surface, (90, 115, 160), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    for x in range(0, WIDTH, 55):
        pygame.draw.line(surface, (38, 48, 72), (x, GROUND_Y + 3), (x - 35, HEIGHT), 1)


# =====================================================
# PARTICLE CLASS
# =====================================================

class Particle:
    def __init__(self, x, y, color, size, lifetime, vx=0, vy=0):
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
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

    def is_dead(self):
        return self.lifetime <= 0 or self.size < 0.5


# =====================================================
# PROJECTILE CLASS
# =====================================================

class Projectile:
    def __init__(self, x, y, direction, element_type, owner, charged=False, vy=0, radius=10, damage=10):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.element_type = element_type
        self.owner = owner
        self.charged = charged

        self.speed = 11 if element_type == 'earth' else (10 if not charged else 14)
        self.radius = radius if not charged else 16
        self.damage = damage if not charged else 20
        self.vy = vy
        self.timer = 100
        self.trail = []
        self.trail_length = 8 if charged else 5

        self.color = ELEMENT_DATA[element_type]['main']
        self.colors = ELEMENT_DATA[element_type]['colors']

        self.rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, particles):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        self.x += self.direction * self.speed
        self.y += self.vy
        self.timer -= 1
        self.rect.center = (int(self.x), int(self.y))

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
        trail_count = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            fade = (i + 1) / (trail_count + 1)
            trail_radius = max(1, int(self.radius * fade * 0.8))
            trail_surf = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
            alpha = int(140 * fade)
            pygame.draw.circle(trail_surf, (*self.color, alpha), (trail_radius, trail_radius), trail_radius)
            surface.blit(trail_surf, (int(tx - trail_radius), int(ty - trail_radius)), special_flags=pygame.BLEND_RGBA_ADD)

        draw_glow(surface, self.x, self.y, self.radius * 2, self.color, 100)

        if self.element_type == 'earth':
            cx, cy = int(self.x), int(self.y)
            pygame.draw.ellipse(
                surface, self.colors[0],
                (cx - self.radius, cy - self.radius // 2, self.radius * 2, self.radius)
            )
            pygame.draw.circle(surface, self.color, (cx, cy), max(2, self.radius - 2))
            pygame.draw.circle(surface, WHITE, (cx + self.direction * 2, cy - 1), max(1, self.radius // 3))

        elif self.element_type == 'fire':
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), max(2, self.radius // 3))

        else:
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
                    False, points, max(2, self.radius // 2)
                )

            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), max(2, self.radius // 3))

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
        self.owner = player
        self.element_type = player.element_type
        self.direction = player.direction

        self.x, self.y = player.get_hand_position()

        self.length = 750
        self.max_width = 36
        self.min_width = 8

        self.timer = 24
        self.max_timer = self.timer

        self.damage = 30
        self.hit_targets = set()

        self.clash_limit = None  # x-coordinate this beam is pushed back to while clashing
        self.clashing = False

        self.animation_time = random.random() * math.tau
        self.particle_timer = 0

        self.colors = ELEMENT_DATA[self.element_type]['colors']
        self.main_color = ELEMENT_DATA[self.element_type]['main']
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
            for _ in range(3):
                distance = random.uniform(0, self.get_live_length())
                px = self.x + self.direction * distance
                py = self.y + random.uniform(-self.max_width * 0.5, self.max_width * 0.5)

                vx = random.uniform(-1, 1)
                vy = random.uniform(-1.5, 1.5)
                size = random.randint(2, 6)

                particles.append(
                    Particle(px, py, random.choice(self.colors), size, 14, vx, vy)
                )

    def get_live_length(self):
        """Full travel length, or the shortened reach while locked in a clash."""
        if self.clash_limit is None:
            return self.length
        return max(0.0, abs(self.clash_limit - self.x))

    def get_live_rect(self):
        """Collision/visual rect clipped to the current clash point, if any."""
        live_length = self.get_live_length()
        rect = pygame.Rect(0, int(self.y - self.max_width // 2), int(live_length), self.max_width)
        if self.direction >= 0:
            rect.left = int(self.x)
        else:
            rect.right = int(self.x)
        return rect

    def is_finished(self):
        return self.timer <= 0

    def draw(self, surface):
        if self.timer <= 0:
            return

        progress = max(0.0, min(1.0, self.timer / self.max_timer))
        fade = min(1.0, (1.0 - progress) * 5 + 0.25)
        pulse = 1.0 + math.sin(self.animation_time * 2) * 0.08
        beam_width = max(self.min_width, int(self.max_width * fade * pulse))

        start_x = self.x
        end_x = start_x + self.direction * self.get_live_length()
        center_y = int(self.y)
        beam_span = abs(end_x - start_x)

        draw_glow(surface, (start_x + end_x) / 2, center_y, beam_width + 14, self.main_color, int(110 * fade))

        # --- Release flare: a wide double-wave burst right at the muzzle,
        # matching the "wings" frame of a freshly unleashed charged attack.
        time_alive = self.max_timer - self.timer
        if time_alive < 10 and beam_span > 4:
            flare_fade = 1.0 - time_alive / 10.0
            flare_size = beam_width * (1.6 + flare_fade * 1.3)
            for side in (-1, 1):
                tip_x = start_x + side * flare_size
                mid_x = start_x + side * flare_size * 0.5
                pts = [
                    (start_x, center_y - beam_width * 0.2),
                    (tip_x, center_y - flare_size * 0.7),
                    (mid_x, center_y),
                    (tip_x, center_y + flare_size * 0.7),
                    (start_x, center_y + beam_width * 0.2),
                ]
                pygame.draw.polygon(surface, self.colors[min(1, len(self.colors) - 1)], pts)
                pygame.draw.polygon(surface, self.highlight, pts, 2)

        # --- Tunnel body: concentric ring segments marching down the beam,
        # giving the drill/auger look of the charged-attack reference art.
        if beam_span > 2:
            ring_spacing = max(9, beam_width * 0.5)
            n_rings = max(1, int(beam_span / ring_spacing))
            for i in range(n_rings + 1):
                t = i / max(1, n_rings)
                rx = start_x + self.direction * t * beam_span
                ring_phase = (self.animation_time * 3 - i * 0.9) % math.tau
                squeeze = 0.55 + 0.3 * math.sin(ring_phase)
                ring_h = max(3, int(beam_width * (0.5 + squeeze * 0.5)))
                ring_w = max(2, int(beam_width * 0.22))
                color = self.colors[i % len(self.colors)]
                pygame.draw.ellipse(
                    surface, color,
                    (int(rx - ring_w / 2), int(center_y - ring_h / 2), ring_w, ring_h)
                )

            pygame.draw.line(surface, self.main_color, (start_x, center_y), (end_x, center_y), max(2, beam_width // 2))

        pygame.draw.line(surface, WHITE, (start_x, center_y), (end_x, center_y), max(1, beam_width // 5))

        # --- Tapering spiral tail as the beam dissipates, echoing the thin
        # corkscrew closing frame of the reference animation.
        if progress < 0.3 and beam_span > 4:
            tail_fade = 1 - progress / 0.3
            tail_len = min(beam_span, beam_width * 2.4 * tail_fade)
            pts = []
            for i in range(16):
                frac = i / 15
                px = end_x - self.direction * frac * tail_len
                spiral_r = (1 - frac) * beam_width * 0.45
                py = center_y + math.sin(self.animation_time * 4 + frac * 10) * spiral_r
                pts.append((int(px), int(py)))
            if len(pts) >= 2:
                pygame.draw.lines(surface, self.highlight, False, pts, max(1, int(beam_width * 0.18)))


# =====================================================
# CLASH EFFECT: the radiant burst/vortex two opposing
# attacks make when they collide mid-air.
# =====================================================

class ClashEffect:
    def __init__(self, x, y, colors, big=False):
        self.x = x
        self.y = y
        self.colors = colors if colors else [WHITE]
        self.max_timer = 16 if big else 11
        self.timer = self.max_timer
        self.start_radius = 6 if big else 3
        self.grow = 2.6 if big else 1.8
        self.spin = random.uniform(0, math.tau)

    def update(self):
        self.timer -= 1

    def is_dead(self):
        return self.timer <= 0

    def draw(self, surface):
        if self.timer <= 0:
            return
        progress = 1.0 - (self.timer / self.max_timer)
        alpha = max(0, int(255 * (1.0 - progress)))
        radius = self.start_radius + progress * self.grow * self.max_timer
        core_r = max(2, int(radius * 0.4))
        ring_r = max(3, int(radius))

        size = ring_r * 4
        fx = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2

        pygame.draw.circle(fx, (255, 255, 255, min(255, alpha)), (c, c), core_r)

        spokes = 8
        for i in range(spokes):
            angle = self.spin + progress * math.pi + i * (math.tau / spokes)
            ex = c + math.cos(angle) * ring_r
            ey = c + math.sin(angle) * ring_r
            col = self.colors[i % len(self.colors)]
            pygame.draw.line(fx, (*col, min(255, alpha)), (c, c), (ex, ey), max(1, int(3 * (1 - progress) + 1)))

        pygame.draw.circle(fx, (*self.colors[0], min(200, alpha)), (c, c), ring_r, 3)
        surface.blit(fx, (int(self.x - c), int(self.y - c)), special_flags=pygame.BLEND_RGBA_ADD)


# =====================================================
# IMPACT JUICE: SCREEN SHAKE & HIT-STOP
# =====================================================

shake_timer = 0.0
shake_intensity = 0.0
hitstop_timer = 0


def trigger_shake(intensity, duration):
    global shake_timer, shake_intensity
    shake_intensity = max(shake_intensity, intensity)
    shake_timer = max(shake_timer, duration)


def trigger_hitstop(frames):
    global hitstop_timer
    hitstop_timer = max(hitstop_timer, frames)


def get_shake_offset():
    if shake_timer <= 0:
        return 0, 0
    power = shake_intensity * (shake_timer / 10.0)
    return int(random.uniform(-power, power)), int(random.uniform(-power, power))


# =====================================================
# CLASH RESOLUTION: opposing attacks fight instead of
# flying past each other. Covers basic shots, barrage
# pellets, and the beam-vs-beam struggle.
# =====================================================

def spawn_clash_burst(particles, clash_effects, x, y, colors, big=False):
    clash_effects.append(ClashEffect(x, y, colors, big=big))
    for _ in range(14 if big else 8):
        particles.append(
            Particle(
                x, y, random.choice(colors), random.randint(3, 7 if big else 5), 14,
                random.uniform(-4, 4), random.uniform(-4, 4),
            )
        )


def resolve_clashes(projectiles, beams, particles, clash_effects):
    for beam in beams:
        beam.clash_limit = None
        beam.clashing = False

    # --- Basic attacks & barrage pellets: opposing bolts cancel each other out ---
    destroyed_ids = set()
    for i, p_a in enumerate(projectiles):
        if id(p_a) in destroyed_ids:
            continue
        for p_b in projectiles[i + 1:]:
            if id(p_b) in destroyed_ids or p_a.owner is p_b.owner:
                continue
            if p_a.rect.colliderect(p_b.rect):
                cx = (p_a.x + p_b.x) / 2
                cy = (p_a.y + p_b.y) / 2
                spawn_clash_burst(particles, clash_effects, cx, cy, p_a.colors + p_b.colors)
                trigger_shake(5, 6)
                destroyed_ids.add(id(p_a))
                destroyed_ids.add(id(p_b))
                break
    if destroyed_ids:
        projectiles[:] = [p for p in projectiles if id(p) not in destroyed_ids]

    # --- A charged beam shreds through any incoming bolt it meets ---
    destroyed_ids = set()
    for proj in projectiles:
        if id(proj) in destroyed_ids:
            continue
        for beam in beams:
            if beam.owner is proj.owner:
                continue
            if proj.rect.colliderect(beam.get_live_rect()):
                spawn_clash_burst(particles, clash_effects, proj.x, proj.y, proj.colors + beam.colors)
                destroyed_ids.add(id(proj))
                break
    if destroyed_ids:
        projectiles[:] = [p for p in projectiles if id(p) not in destroyed_ids]

    # --- Beam vs beam: a pushing struggle, contact point biased by the
    # elemental type matchup, like two charged attacks locking together. ---
    for i, b_a in enumerate(beams):
        for b_b in beams[i + 1:]:
            if b_a.owner is b_b.owner:
                continue
            if not b_a.rect.colliderect(b_b.rect):
                continue
            overlap = b_a.rect.clip(b_b.rect)
            if overlap.width <= 0:
                continue

            power_a = b_a.damage * get_type_multiplier(b_a.element_type, b_b.element_type)
            power_b = b_b.damage * get_type_multiplier(b_b.element_type, b_a.element_type)
            total = power_a + power_b
            bias = ((power_a - power_b) / total) if total else 0.0
            bias += random.uniform(-0.08, 0.08)
            bias = max(-0.9, min(0.9, bias))

            contact_x = overlap.centerx + bias * (overlap.width / 2)
            b_a.clash_limit = contact_x
            b_b.clash_limit = contact_x
            b_a.clashing = True
            b_b.clashing = True

            if random.random() < 0.5:
                spawn_clash_burst(particles, clash_effects, contact_x, (b_a.y + b_b.y) / 2, b_a.colors + b_b.colors, big=True)
            trigger_shake(3, 4)


# =====================================================
# PLAYER CLASS
# =====================================================

class Player:
    def __init__(self, x, y, element_type, is_player_one):
        self.x = float(x)
        self.y = float(y)
        self.element_type = element_type
        self.is_player_one = is_player_one

        self.hp = 100
        self.display_hp = 100
        self.speed = 5

        self.max_stamina = 100.0
        self.stamina = 100.0
        self.stamina_regen = 100.0 / 600.0
        
        self.shield_timer = 0
        self.shield_cooldown = 0  # 2 seconds cooldown (120 frames)

        self.charging = False
        self.charge_time = 0
        self.charge_threshold = 45

        self.barrage_queue = 0
        self.barrage_cooldown = 0

        self.animation_time = random.random() * math.tau
        self.hit_flash = 0

        self.direction = 1 if is_player_one else -1

        self.attack_timer = 0
        self.attack_duration = 18
        self.attack_flash = 0
        self.min_attack_cost = self.max_stamina / 6.0

        self.knockback_vx = 0.0
        self.squash_amount = 0.0
        self.walk_phase = 0.0
        self.bob_amp = 0.0
        self.lean = 0.0
        self.is_moving = False

        self.color = ELEMENT_DATA[element_type]['main']
        self.colors = ELEMENT_DATA[element_type]['colors']

        self.rect = pygame.Rect(int(x - 20), int(y - 45), 40, 75)

    def move(self, up_key, down_key, left_key, right_key, keys):
        dx = 0
        dy = 0
        if keys[up_key]:
            dy -= 1
        if keys[down_key]:
            dy += 1
        if keys[left_key]:
            dx -= 1
        if keys[right_key]:
            dx += 1

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Knockback impulse from being hit, decaying each frame
        self.x += self.knockback_vx
        self.knockback_vx *= 0.82
        if abs(self.knockback_vx) < 0.1:
            self.knockback_vx = 0.0

        self.y = max(125, min(GROUND_Y - 45, self.y))

        if self.is_player_one:
            self.x = max(60, min(WIDTH // 2 - 60, self.x))
        else:
            self.x = max(WIDTH // 2 + 60, min(WIDTH - 60, self.x))

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Walk bob + lean-into-movement feel
        self.is_moving = dx != 0 or dy != 0
        if self.is_moving:
            self.walk_phase += 0.4
        target_bob_amp = 1.0 if self.is_moving else 0.0
        self.bob_amp += (target_bob_amp - self.bob_amp) * 0.25

        target_lean = dx
        self.lean += (target_lean - self.lean) * 0.2

    def trigger_shield(self):
        shield_cost = self.max_stamina / 5.0
        if self.shield_cooldown <= 0 and self.shield_timer <= 0 and self.stamina >= shield_cost:
            self.stamina -= shield_cost
            self.shield_timer = 30  # Active for 0.5 seconds
            self.shield_cooldown = 120  # 2 seconds cooldown at 60 FPS
            self.squash_amount = -0.25

    def trigger_barrage(self, projectiles):
        barrage_cost = 30.0
        if self.barrage_cooldown <= 0 and self.barrage_queue == 0 and self.stamina >= barrage_cost:
            self.stamina -= barrage_cost
            self.barrage_queue = 6 if self.element_type == 'earth' else 5
            self.barrage_cooldown = 120

    def update(self, particles, projectiles):
        self.animation_time += 0.12

        self.display_hp += (self.hp - self.display_hp) * 0.12
        if abs(self.hp - self.display_hp) < 0.1:
            self.display_hp = self.hp

        self.squash_amount *= 0.78
        if abs(self.squash_amount) < 0.01:
            self.squash_amount = 0.0

        if not self.charging and self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)

        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1

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
                self.attack_timer = 5
                self.attack_flash = 4
                self.barrage_queue -= 1

                hand_x, hand_y = self.get_hand_position()
                spread_vy = random.uniform(-2.2, 2.2)

                projectiles.append(
                    Projectile(
                        hand_x, hand_y, self.direction, self.element_type, self,
                        charged=False, vy=spread_vy,
                        radius=6 if self.element_type == 'earth' else 7,
                        damage=4 if self.element_type == 'earth' else 5,
                    )
                )

        if not self.charging:
            return

        self.charge_time += 1
        progress = min(1.0, self.charge_time / self.charge_threshold)
        hand_x, hand_y = self.get_hand_position()

        for _ in range(2):
            angle = random.uniform(0, math.tau)
            radius = random.uniform(20, 38 + progress * 15)
            px = hand_x + math.cos(angle) * radius
            py = hand_y + math.sin(angle) * radius
            vx = (hand_x - px) * 0.08
            vy = (hand_y - py) * 0.08

            particles.append(
                Particle(px, py, random.choice(self.colors), random.randint(3, 6), 16, vx, vy)
            )

    def take_damage(self, damage, attacker_direction=0):
        if self.shield_timer > 0:
            return
        self.hp = max(0, self.hp - damage)
        self.hit_flash = 12
        self.squash_amount = -0.4
        self.knockback_vx += attacker_direction * 8.0

        trigger_shake(min(14, 4 + damage * 0.5), 10)
        trigger_hitstop(7 if damage >= 15 else 3)

    def get_hand_position(self):
        shoulder_x = self.x + self.direction * 12
        shoulder_y = self.y - 14
        sway = math.sin(self.animation_time * 2.5) * 2

        if self.charging:
            progress = min(1.0, self.charge_time / self.charge_threshold)
            eased = progress * progress * (3 - 2 * progress)
            hand_x = shoulder_x - self.direction * (17 + eased * 18)
            hand_y = shoulder_y + 15 + eased * 5 + sway
        elif self.attack_timer > 0:
            hand_x = shoulder_x + self.direction * 38
            hand_y = shoulder_y - 2
        else:
            hand_x = shoulder_x + self.direction * 18
            hand_y = shoulder_y + 14 + sway

        return hand_x, hand_y

    def release_attack(self):
        charged = self.charge_time >= self.charge_threshold
        self.charging = False
        self.charge_time = 0

        cost = 25.0 if charged else self.min_attack_cost

        if self.stamina >= cost:
            self.stamina -= cost
            self.attack_timer = self.attack_duration
            self.attack_flash = 7
            self.squash_amount = 0.45 if charged else 0.25

            if charged:
                recoil_distance = 22
                self.x -= self.direction * recoil_distance
                if self.is_player_one:
                    self.x = max(60, min(WIDTH // 2 - 60, self.x))
                else:
                    self.x = max(WIDTH // 2 + 60, min(WIDTH - 60, self.x))
                self.rect.centerx = int(self.x)

                return Beam(self)

            hand_x, hand_y = self.get_hand_position()
            return Projectile(
                hand_x, hand_y, self.direction, self.element_type, self,
                charged=False, radius=8, damage=10
            )
        return None

    def draw(self, surface, opponent):
        self.direction = 1 if opponent.x > self.x else -1

        main_color = self.color
        highlight = self.colors[-1]

        if self.hit_flash > 0 and (self.hit_flash // 2) % 2 == 0:
            main_color = WHITE

        t = self.animation_time
        breathe = math.sin(t * 2) * 2

        # Walk bob (lifts the upper body slightly on each step) and a lean
        # into the direction of movement.
        bob = -abs(math.sin(self.walk_phase)) * 4 * self.bob_amp
        lean_x = self.lean * 5

        upper_y = self.y + bob
        shoulder_y = upper_y - 14
        head_y = upper_y - 43 + breathe * 0.3 + lean_x * 0.3

        # Squash-and-stretch pulse (attacks stretch, impacts/shield compress),
        # anchored to the feet so it reads as a pop rather than a float.
        s = self.squash_amount
        body_w = 28 * (1 - s * 0.6)
        body_h = 44 * (1 + s * 0.6)
        body_bottom = upper_y + 17 + breathe * 0.3
        body_top = body_bottom - body_h
        body_rect = pygame.Rect(int(self.x - body_w / 2 + lean_x * 0.4), int(body_top), int(body_w), int(body_h))

        if self.charging:
            progress = min(1.0, self.charge_time / self.charge_threshold)
            hand_x, hand_y = self.get_hand_position()
            draw_glow(surface, hand_x, hand_y, 16 + progress * 42, main_color, int(70 + progress * 150))

        if self.shield_timer > 0:
            draw_honeycomb_shield(surface, self.x, upper_y - 5, 46)

        pygame.draw.rect(surface, BLACK, (int(self.x - 10), int(self.y + 17), 8, 28))
        pygame.draw.rect(surface, main_color, (int(self.x - 9), int(self.y + 18), 6, 26))
        pygame.draw.rect(surface, BLACK, (int(self.x + 2), int(self.y + 17), 8, 28))
        pygame.draw.rect(surface, main_color, (int(self.x + 3), int(self.y + 18), 6, 26))

        pygame.draw.rect(surface, BLACK, (body_rect.x - 2, body_rect.y - 2, body_rect.width + 4, body_rect.height + 4), border_radius=10)
        pygame.draw.rect(surface, main_color, body_rect, border_radius=8)

        pygame.draw.circle(surface, BLACK, (int(self.x + lean_x), int(head_y)), 15)
        pygame.draw.circle(surface, main_color, (int(self.x + lean_x), int(head_y)), 13)
        pygame.draw.circle(surface, BLACK, (int(self.x + lean_x + self.direction * 5), int(head_y - 1)), 3)

        hand_x, hand_y = self.get_hand_position()
        pygame.draw.line(surface, BLACK, (self.x, shoulder_y), (hand_x, hand_y), 10)
        pygame.draw.line(surface, highlight, (self.x, shoulder_y), (hand_x, hand_y), 7)
        pygame.draw.circle(surface, WHITE, (int(hand_x), int(hand_y)), 6)


# =====================================================
# UI HELPERS & SELECTION SCREEN
# =====================================================

def draw_health_and_stamina_bar(surface, x, y, player, label):
    width = 380
    height = 20

    pygame.draw.rect(surface, (55, 35, 50), (x, y, width, height), border_radius=6)
    health_width = int(width * max(0, player.display_hp) / 100)

    if health_width > 0:
        pygame.draw.rect(surface, player.color, (x, y, health_width, height), border_radius=6)

    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2, border_radius=6)
    text = FONT.render(f"{label}: {int(player.hp)} HP", True, WHITE)
    surface.blit(text, (x, y - 26))

    stamina_y = y + height + 6
    stamina_height = 10
    pygame.draw.rect(surface, (40, 45, 65), (x, stamina_y, width, stamina_height), border_radius=4)
    stamina_width = int(width * max(0, player.stamina) / 100.0)

    if stamina_width > 0:
        pygame.draw.rect(surface, (230, 200, 50), (x, stamina_y, stamina_width, stamina_height), border_radius=4)
    pygame.draw.rect(surface, WHITE, (x, stamina_y, width, stamina_height), 1, border_radius=4)

    # Display Shield Cooldown indicator if cooling down
    if player.shield_cooldown > 0:
        cd_secs = math.ceil(player.shield_cooldown / 60)
        cd_text = SMALL_FONT.render(f"Shield CD: {cd_secs}s", True, (200, 150, 150))
        surface.blit(cd_text, (x + width - cd_text.get_width(), y - 26))


class ElementScrollbar:
    """A horizontal scrollbar/slider for picking an element: drag the thumb,
    click anywhere on the track to jump, or snap it via keyboard."""

    def __init__(self, x, y, width, height, elements):
        self.rect = pygame.Rect(x, y, width, height)
        self.elements = elements
        self.count = len(elements)
        self.segment_width = width / self.count
        self.index = 0
        self.dragging = False

    def _index_from_x(self, mx):
        rel = mx - self.rect.x
        idx = int(rel // self.segment_width)
        return max(0, min(self.count - 1, idx))

    def set_index(self, idx):
        self.index = max(0, min(self.count - 1, idx))

    def handle_event(self, event):
        """Returns True if the selection changed."""
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                new_idx = self._index_from_x(event.pos[0])
                if new_idx != self.index:
                    self.index = new_idx
                    changed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_idx = self._index_from_x(event.pos[0])
            if new_idx != self.index:
                self.index = new_idx
                changed = True
        return changed

    def draw(self, surface, thumb_color, mouse_pos):
        # Track
        pygame.draw.rect(surface, (26, 32, 52), self.rect, border_radius=self.rect.height // 2)
        pygame.draw.rect(surface, (95, 115, 150), self.rect, 2, border_radius=self.rect.height // 2)

        # Segment divider ticks + labels
        for i in range(self.count):
            seg_x = self.rect.x + i * self.segment_width
            if i > 0:
                pygame.draw.line(
                    surface, (70, 85, 115),
                    (seg_x, self.rect.y + 5), (seg_x, self.rect.bottom - 5), 2
                )
            label = SMALL_FONT.render(ELEMENT_DATA[self.elements[i]]['name'], True, (210, 220, 240))
            label_x = seg_x + self.segment_width / 2 - label.get_width() / 2
            surface.blit(label, (label_x, self.rect.bottom + 6))

        # Thumb
        thumb_w = self.segment_width - 10
        thumb_x = self.rect.x + self.index * self.segment_width + 5
        thumb_rect = pygame.Rect(int(thumb_x), self.rect.y - 5, int(thumb_w), self.rect.height + 10)
        hovered = thumb_rect.collidepoint(mouse_pos) or self.dragging
        pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE if hovered else (210, 220, 240), thumb_rect, 3, border_radius=10)


class CharacterSelectionScreen:
    def __init__(self):
        self.elements = ['fire', 'water', 'earth']

        self.p1_card_rect = pygame.Rect(100, 160, 360, 320)
        self.p2_card_rect = pygame.Rect(640, 160, 360, 320)
        self.start_btn_rect = pygame.Rect(WIDTH // 2 - 180, 540, 360, 50)

        self.p1_scrollbar = ElementScrollbar(
            self.p1_card_rect.x + 30, self.p1_card_rect.y + 215, self.p1_card_rect.width - 60, 36, self.elements
        )
        self.p2_scrollbar = ElementScrollbar(
            self.p2_card_rect.x + 30, self.p2_card_rect.y + 215, self.p2_card_rect.width - 60, 36, self.elements
        )
        self.p2_scrollbar.set_index(1)

    @property
    def p1_idx(self):
        return self.p1_scrollbar.index

    @property
    def p2_idx(self):
        return self.p2_scrollbar.index

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.p1_scrollbar.set_index((self.p1_scrollbar.index - 1) % len(self.elements))
            elif event.key == pygame.K_d:
                self.p1_scrollbar.set_index((self.p1_scrollbar.index + 1) % len(self.elements))

            elif event.key == pygame.K_LEFT:
                self.p2_scrollbar.set_index((self.p2_scrollbar.index - 1) % len(self.elements))
            elif event.key == pygame.K_RIGHT:
                self.p2_scrollbar.set_index((self.p2_scrollbar.index + 1) % len(self.elements))

            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_btn_rect.collidepoint(event.pos):
                return True

        self.p1_scrollbar.handle_event(event)
        self.p2_scrollbar.handle_event(event)

        return False

    def draw(self, surface):
        surface.fill(BG)
        title = TITLE_FONT.render("SELECT YOUR ELEMENT", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        pygame.draw.line(surface, (50, 65, 95), (WIDTH // 2, 120), (WIDTH // 2, 500), 3)

        mouse_pos = pygame.mouse.get_pos()
        mx, my = mouse_pos

        # P1 Box
        p1_elem = self.elements[self.p1_idx]
        p1_data = ELEMENT_DATA[p1_elem]
        p1_hover = self.p1_card_rect.collidepoint(mx, my)

        pygame.draw.rect(surface, p1_data['main'], self.p1_card_rect, border_radius=16)
        pygame.draw.rect(surface, (255, 255, 255) if p1_hover else (180, 200, 230), self.p1_card_rect, 6 if p1_hover else 4, border_radius=16)

        p1_title = TITLE_FONT.render("PLAYER 1", True, WHITE)
        p1_elem_txt = LARGE_FONT.render(p1_data['name'], True, WHITE)
        p1_hint = FONT.render("Drag the bar or press A / D", True, (220, 235, 255))

        surface.blit(p1_title, (280 - p1_title.get_width() // 2, 180))
        surface.blit(p1_elem_txt, (280 - p1_elem_txt.get_width() // 2, 260))
        self.p1_scrollbar.draw(surface, p1_data['main'], mouse_pos)
        surface.blit(p1_hint, (280 - p1_hint.get_width() // 2, 465))

        # P2 Box
        p2_elem = self.elements[self.p2_idx]
        p2_data = ELEMENT_DATA[p2_elem]
        p2_hover = self.p2_card_rect.collidepoint(mx, my)

        pygame.draw.rect(surface, p2_data['main'], self.p2_card_rect, border_radius=16)
        pygame.draw.rect(surface, (255, 255, 255) if p2_hover else (180, 200, 230), self.p2_card_rect, 6 if p2_hover else 4, border_radius=16)

        p2_title = TITLE_FONT.render("PLAYER 2", True, WHITE)
        p2_elem_txt = LARGE_FONT.render(p2_data['name'], True, WHITE)
        p2_hint = FONT.render("Drag the bar or press LEFT / RIGHT", True, (220, 235, 255))

        surface.blit(p2_title, (820 - p2_title.get_width() // 2, 180))
        surface.blit(p2_elem_txt, (820 - p2_elem_txt.get_width() // 2, 260))
        self.p2_scrollbar.draw(surface, p2_data['main'], mouse_pos)
        surface.blit(p2_hint, (820 - p2_hint.get_width() // 2, 465))

        # Start Button
        btn_hover = self.start_btn_rect.collidepoint(mx, my)
        btn_color = (60, 180, 90) if btn_hover else (40, 140, 70)

        pygame.draw.rect(surface, btn_color, self.start_btn_rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.start_btn_rect, 2, border_radius=12)

        start_txt = FONT.render("CLICK HERE TO START BATTLE", True, WHITE)
        surface.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, 552))


# =====================================================
# GAME INITIALIZATION
# =====================================================

selection_screen = CharacterSelectionScreen()
state = "SELECTION"

player1 = None
player2 = None
projectiles = []
beams = []
particles = []
clash_effects = []

game_over = False
winner_text = ""
background_time = 0.0

running = True

# =====================================================
# MAIN GAME LOOP
# =====================================================

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if state == "SELECTION":
            if selection_screen.handle_input(event):
                p1_elem = selection_screen.elements[selection_screen.p1_idx]
                p2_elem = selection_screen.elements[selection_screen.p2_idx]

                player1 = Player(200, 400, p1_elem, True)
                player2 = Player(900, 400, p2_elem, False)
                state = "BATTLE"

        elif state == "BATTLE":
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    state = "SELECTION"
                    game_over = False
                    projectiles.clear()
                    beams.clear()
                    particles.clear()
                    clash_effects.clear()

                elif not game_over:
                    # P1 Controls
                    if event.key == pygame.K_e:
                        player1.trigger_shield()
                    elif event.key == pygame.K_f:
                        if player1.stamina >= player1.min_attack_cost:
                            player1.charging = True
                            player1.charge_time = 0
                    elif event.key == pygame.K_g:
                        player1.trigger_barrage(projectiles)

                    # P2 Controls
                    elif event.key == pygame.K_RCTRL:
                        player2.trigger_shield()
                    elif event.key == pygame.K_RETURN:
                        if player2.stamina >= player2.min_attack_cost:
                            player2.charging = True
                            player2.charge_time = 0
                    elif event.key == pygame.K_RSHIFT:
                        player2.trigger_barrage(projectiles)

            elif event.type == pygame.KEYUP and not game_over:
                if event.key == pygame.K_f and player1.charging:
                    attack = player1.release_attack()
                    if isinstance(attack, Beam):
                        beams.append(attack)
                    elif isinstance(attack, Projectile):
                        projectiles.append(attack)

                elif event.key == pygame.K_RETURN and player2.charging:
                    attack = player2.release_attack()
                    if isinstance(attack, Beam):
                        beams.append(attack)
                    elif isinstance(attack, Projectile):
                        projectiles.append(attack)

    # -------------------------------------------------
    # SELECTION STATE
    # -------------------------------------------------
    if state == "SELECTION":
        selection_screen.draw(screen)

    # -------------------------------------------------
    # BATTLE STATE
    # -------------------------------------------------
    elif state == "BATTLE":
        if not game_over:
            if hitstop_timer > 0:
                # Freeze-frame on a big hit: skip gameplay updates for a
                # few frames so the impact reads as a punch, not a blip.
                hitstop_timer -= 1
            else:
                keys = pygame.key.get_pressed()
                player1.move(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, keys)
                player2.move(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, keys)

                background_time += 0.02

                for p in particles[:]:
                    p.update()
                    if p.is_dead():
                        particles.remove(p)

                for ce in clash_effects[:]:
                    ce.update()
                    if ce.is_dead():
                        clash_effects.remove(ce)

                # Advance every in-flight attack first...
                for proj in projectiles[:]:
                    proj.update(particles)
                    if proj.is_finished():
                        projectiles.remove(proj)

                for beam in beams[:]:
                    beam.update(particles)
                    if beam.is_finished():
                        beams.remove(beam)

                # ...then let opposing attacks clash before checking whether
                # anything that's left actually reaches a player. This covers
                # basic attacks and barrage pellets (mutual cancel-out), a
                # beam shredding an incoming bolt, and beam-vs-beam struggles.
                resolve_clashes(projectiles, beams, particles, clash_effects)

                # Projectiles
                for proj in projectiles[:]:
                    target = player2 if proj.owner is player1 else player1
                    if proj.rect.colliderect(target.rect):
                        multiplier = get_type_multiplier(proj.element_type, target.element_type)
                        final_damage = int(proj.damage * multiplier)
                        target.take_damage(final_damage, proj.direction)

                        for _ in range(8):
                            particles.append(
                                Particle(
                                    proj.x, proj.y,
                                    random.choice(proj.colors),
                                    random.randint(2, 5), 12,
                                    random.uniform(-2, 2),
                                    random.uniform(-2, 2)
                                )
                            )
                        projectiles.remove(proj)

                # Beams (use the live, clash-clipped reach so a beam locked
                # in a struggle can't hit a player until it breaks through)
                for beam in beams:
                    target = player2 if beam.owner is player1 else player1
                    if beam.get_live_rect().colliderect(target.rect) and target not in beam.hit_targets:
                        multiplier = get_type_multiplier(beam.element_type, target.element_type)
                        final_damage = int(beam.damage * multiplier)
                        target.take_damage(final_damage, beam.direction)
                        beam.hit_targets.add(target)

                        for _ in range(16):
                            particles.append(
                                Particle(
                                    target.x, target.y,
                                    random.choice(beam.colors + [WHITE]),
                                    random.randint(3, 8), 16,
                                    random.uniform(-4, 4),
                                    random.uniform(-4, 4)
                                )
                            )

                player1.update(particles, projectiles)
                player2.update(particles, projectiles)

                if player1.hp <= 0:
                    game_over = True
                    winner_text = f"Player 2 ({ELEMENT_DATA[player2.element_type]['name']}) Wins!"
                elif player2.hp <= 0:
                    game_over = True
                    winner_text = f"Player 1 ({ELEMENT_DATA[player1.element_type]['name']}) Wins!"

            if shake_timer > 0:
                shake_timer -= 1

        # Drawing Battle (rendered to an offscreen surface so a screen
        # shake can nudge the whole scene without affecting UI/game logic)
        draw_background(game_surface, background_time)

        for p in particles:
            p.draw(game_surface)

        for proj in projectiles:
            proj.draw(game_surface)

        for beam in beams:
            beam.draw(game_surface)

        for ce in clash_effects:
            ce.draw(game_surface)

        player1.draw(game_surface, player2)
        player2.draw(game_surface, player1)

        # Health & Stamina Bars
        draw_health_and_stamina_bar(game_surface, 60, 45, player1, f"P1: {ELEMENT_DATA[player1.element_type]['name']}")
        draw_health_and_stamina_bar(game_surface, 660, 45, player2, f"P2: {ELEMENT_DATA[player2.element_type]['name']}")

        # Move Guides at Bottom
        p1_move_desc = ELEMENT_DATA[player1.element_type]['p1_controls']
        p2_move_desc = ELEMENT_DATA[player2.element_type]['p2_controls']

        p1_hud = SMALL_FONT.render(p1_move_desc, True, ELEMENT_DATA[player1.element_type]['colors'][-1])
        p2_hud = SMALL_FONT.render(p2_move_desc, True, ELEMENT_DATA[player2.element_type]['colors'][-1])

        game_surface.blit(p1_hud, (60, HEIGHT - 30))
        game_surface.blit(p2_hud, (WIDTH - p2_hud.get_width() - 60, HEIGHT - 30))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 14, 25, 180))
            game_surface.blit(overlay, (0, 0))

            win_surf = LARGE_FONT.render(winner_text, True, WHITE)
            restart_surf = FONT.render("Press 'R' to Select New Elements or ESC to Exit", True, (200, 220, 255))

            game_surface.blit(win_surf, (WIDTH // 2 - win_surf.get_width() // 2, HEIGHT // 2 - 50))
            game_surface.blit(restart_surf, (WIDTH // 2 - restart_surf.get_width() // 2, HEIGHT // 2 + 20))

        shake_x, shake_y = get_shake_offset()
        screen.fill(BG)
        screen.blit(game_surface, (shake_x, shake_y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
