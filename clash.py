import math
import random
import sys
import time
import io
import wave
import struct
import threading
import pygame

pygame.init()

# =====================================================
# GAME CONFIGURATION & CONSTANTS
# =====================================================

WIDTH, HEIGHT = 1200, 700
GROUND_Y = 550
FPS = 60

# Screen & Surfaces
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ELEMENTAL CLASH: OVERDRIVE - Full Fledged Edition")
clock = pygame.time.Clock()

game_surface = pygame.Surface((WIDTH, HEIGHT))
ui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Palette
WHITE = (245, 250, 255)
BLACK = (12, 14, 24)
DARK_BG = (10, 13, 26)
GOLD = (255, 215, 60)
CRIT_RED = (255, 65, 65)

# Fonts
try:
    HUGE_FONT = pygame.font.SysFont("impact", 64)
    TITLE_FONT = pygame.font.SysFont("impact", 48)
    HEADER_FONT = pygame.font.SysFont("arial", 28, bold=True)
    FONT = pygame.font.SysFont("arial", 20, bold=True)
    SMALL_FONT = pygame.font.SysFont("arial", 14, bold=True)
    TINY_FONT = pygame.font.SysFont("arial", 11, bold=True)
except Exception:
    HUGE_FONT = pygame.font.Font(None, 64)
    TITLE_FONT = pygame.font.Font(None, 48)
    HEADER_FONT = pygame.font.Font(None, 28)
    FONT = pygame.font.Font(None, 20)
    SMALL_FONT = pygame.font.Font(None, 14)
    TINY_FONT = pygame.font.Font(None, 11)

# =====================================================
# ELEMENTAL DATA & MOVE SET DEFINITIONS
# =====================================================

ELEMENT_DATA = {
    'fire': {
        'name': 'IGNIS',
        'title': 'The Flame Colossus',
        'main': (245, 60, 25),
        'accent': (255, 145, 30),
        'highlight': (255, 230, 75),
        'core': (255, 250, 210),
        'dark': (70, 16, 10),
        'colors': [(245, 60, 25), (255, 145, 30), (255, 220, 60), (255, 250, 200)],
        'stats': {'power': 95, 'speed': 70, 'defense': 65, 'range': 80},
        'primary_name': 'Solar Comet',
        'skill_name': 'Inferno Volley',
        'beam_name': 'Solar Flare Ray',
        'ult_name': 'SUPERNOVA APOCALYPSE',
        'desc': 'Devastating offensive firepower with high burst damage and burning trails.'
    },
    'water': {
        'name': 'AQUARIS',
        'title': 'The Ocean Sovereign',
        'main': (25, 120, 245),
        'accent': (35, 190, 255),
        'highlight': (120, 235, 255),
        'core': (230, 250, 255),
        'dark': (12, 35, 80),
        'colors': [(20, 95, 235), (35, 190, 255), (120, 235, 255), (225, 250, 255)],
        'stats': {'power': 75, 'speed': 85, 'defense': 80, 'range': 85},
        'primary_name': 'Hydro Lance',
        'skill_name': 'Torrent Surge',
        'beam_name': 'Tidal Maelstrom',
        'ult_name': 'LEVIATHAN DELUGE',
        'desc': 'Fluid mobility, rapid piercing barrages, and immense tsunami waves.'
    },
    'earth': {
        'name': 'TERRAN',
        'title': 'The Stone Vanguard',
        'main': (45, 175, 65),
        'accent': (75, 225, 95),
        'highlight': (165, 245, 130),
        'core': (230, 255, 205),
        'dark': (15, 60, 25),
        'colors': [(35, 140, 50), (65, 210, 85), (150, 240, 120), (220, 255, 190)],
        'stats': {'power': 85, 'speed': 60, 'defense': 95, 'range': 75},
        'primary_name': 'Geo Boulder',
        'skill_name': 'Fissure Spikes',
        'beam_name': 'Tectonic Cannon',
        'ult_name': 'CATACLYSMIC QUAKE',
        'desc': 'Heavy bastion armor, ground-erupting crystals, and crushing monoliths.'
    },
    'lightning': {
        'name': 'VOLT',
        'title': 'The Storm Striker',
        'main': (160, 45, 255),
        'accent': (35, 225, 255),
        'highlight': (140, 240, 255),
        'core': (250, 255, 255),
        'dark': (45, 15, 80),
        'colors': [(160, 45, 255), (60, 160, 255), (50, 235, 255), (250, 255, 255)],
        'stats': {'power': 90, 'speed': 95, 'defense': 55, 'range': 85},
        'primary_name': 'Plasma Bolt',
        'skill_name': 'Chain Discharge',
        'beam_name': 'Thunder God Railgun',
        'ult_name': 'JUDGMENT OF RAIJIN',
        'desc': 'Blistering speed, instantaneous electric bolts, and cascading thunderbolts.'
    },
    'wind': {
        'name': 'ZEPHYR',
        'title': 'The Gale Sylph',
        'main': (20, 195, 170),
        'accent': (65, 240, 205),
        'highlight': (180, 255, 240),
        'core': (245, 255, 252),
        'dark': (10, 65, 55),
        'colors': [(20, 180, 155), (65, 235, 200), (170, 250, 235), (240, 255, 250)],
        'stats': {'power': 70, 'speed': 100, 'defense': 65, 'range': 90},
        'primary_name': 'Gale Crescent',
        'skill_name': 'Whirlwind Burst',
        'beam_name': 'Vortex Hurricane',
        'ult_name': 'TEMPEST CATACLYSM',
        'desc': 'Extreme aerial agility, sonic slicing blades, and twin raging tornados.'
    }
}

ELEMENT_LIST = ['fire', 'water', 'earth', 'lightning', 'wind']

# Type Effectiveness Matchup Multipliers
TYPE_MATCHUPS = {
    'fire': {'earth': 1.5, 'wind': 1.5, 'water': 0.75},
    'water': {'fire': 1.5, 'earth': 1.25, 'lightning': 0.75},
    'earth': {'water': 1.5, 'lightning': 1.5, 'fire': 0.75, 'wind': 0.75},
    'lightning': {'water': 1.5, 'wind': 1.5, 'earth': 0.75},
    'wind': {'earth': 1.5, 'fire': 1.25, 'lightning': 0.75},
}

def get_type_multiplier(attacker_type, defender_type):
    return TYPE_MATCHUPS.get(attacker_type, {}).get(defender_type, 1.0)


# =====================================================
# PROCEDURAL AUDIO SYNTHESIZER
# =====================================================

class SoundEngine:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.music_enabled = True
        self.volume_sfx = 0.7
        self.volume_music = 0.4
        self.music_channel = None
        self.sample_rate = 22050
        self.ready = False

        try:
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
            self.music_channel = pygame.mixer.Channel(7)
            self.init_sfx()
            self.ready = True
        except Exception as e:
            print("Mixer init failed, running silent:", e)
            self.enabled = False

    def _pack_sound(self, dur, fn):
        n = int(self.sample_rate * dur)
        frames = []
        for i in range(n):
            t = i / float(self.sample_rate)
            val = int(max(-32767, min(32767, fn(t, dur) * 32000)))
            frames.append(struct.pack('<hh', val, val))
        buf = io.BytesIO()
        w = wave.open(buf, 'wb')
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(self.sample_rate)
        w.writeframes(b''.join(frames))
        w.close()
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def init_sfx(self):
        # Primary shoot
        self.sounds['shoot'] = self._pack_sound(0.12, lambda t, d: math.sin(2 * math.pi * (820 - 450 * (t/d)) * t) * (1 - t/d))
        # Heavy impact hit
        self.sounds['hit'] = self._pack_sound(0.20, lambda t, d: (math.sin(2 * math.pi * 95 * t) + ((hash(int(t * 14000)) % 100) / 50.0 - 1.0) * 0.35) * (1 - t/d))
        # Beam firing hum & roar
        self.sounds['beam'] = self._pack_sound(0.40, lambda t, d: (math.sin(2 * math.pi * 140 * t) * 0.5 + math.sin(2 * math.pi * 280 * t) * 0.3 + ((hash(int(t * 22000)) % 100) / 50.0 - 1.0) * 0.25) * math.sin(math.pi * t / d))
        # Charge hum
        self.sounds['charge'] = self._pack_sound(0.25, lambda t, d: math.sin(2 * math.pi * (200 + 600 * (t/d)**1.5) * t) * 0.4 * (t/d))
        # Perfect parry - crisp crystal chime
        self.sounds['parry'] = self._pack_sound(0.45, lambda t, d: (math.sin(2 * math.pi * 1450 * t) * 0.65 + math.sin(2 * math.pi * 2150 * t) * 0.35) * math.exp(-7.5 * t))
        # Shield barrier activation
        self.sounds['shield'] = self._pack_sound(0.22, lambda t, d: math.sin(2 * math.pi * (300 + 150 * math.sin(t * 40)) * t) * (1 - t/d) * 0.5)
        # Dash whoosh
        self.sounds['dash'] = self._pack_sound(0.15, lambda t, d: ((hash(int(t * 16000)) % 100) / 50.0 - 1.0) * math.sin(math.pi * t / d) * 0.45)
        # Clash crackle
        self.sounds['clash'] = self._pack_sound(0.18, lambda t, d: (math.sin(2 * math.pi * 320 * t) * 0.4 + ((hash(int(t * 30000)) % 100) / 50.0 - 1.0) * 0.4) * (1 - t/d))
        # Ultimate / Overdrive thunder
        self.sounds['ultimate'] = self._pack_sound(0.65, lambda t, d: (math.sin(2 * math.pi * (80 + 120 * (1 - t/d)) * t) * 0.7 + ((hash(int(t * 18000)) % 100) / 50.0 - 1.0) * 0.4) * (1 - (t/d)**0.6))
        # UI Clicks
        self.sounds['select'] = self._pack_sound(0.08, lambda t, d: math.sin(2 * math.pi * 880 * t) * (1 - t/d) * 0.4)
        self.sounds['move'] = self._pack_sound(0.05, lambda t, d: math.sin(2 * math.pi * 440 * t) * (1 - t/d) * 0.3)
        self.sounds['ko'] = self._pack_sound(0.8, lambda t, d: (math.sin(2 * math.pi * (160 - 90 * (t/d)) * t) * 0.7 + ((hash(int(t * 12000)) % 100) / 50.0 - 1.0) * 0.3) * (1 - t/d))

        for snd in self.sounds.values():
            snd.set_volume(self.volume_sfx)

        # Procedural Background Music Loop (125 BPM synth loop)
        try:
            self.music_sound = self._generate_music_loop()
            self.music_sound.set_volume(self.volume_music)
            if self.music_enabled and self.music_channel:
                self.music_channel.play(self.music_sound, loops=-1)
        except Exception as e:
            print("Music synth skipped:", e)

    def _generate_music_loop(self):
        dur = 3.84  # 8 beats at 125 BPM
        n = int(self.sample_rate * dur)
        frames = []
        bpm = 125.0
        beat_dur = 60.0 / bpm
        bass_notes = [55.0, 55.0, 65.4, 49.0]  # A, A, C, G

        for i in range(n):
            t = i / float(self.sample_rate)
            beat_time = (t % beat_dur) / beat_dur
            beat_num = int(t / beat_dur) % 8

            # Kick drum on beats 0, 2, 4, 6
            kick = 0.0
            if beat_num % 2 == 0 and beat_time < 0.2:
                freq = 140.0 * math.exp(-beat_time * 24.0)
                kick = math.sin(2 * math.pi * freq * beat_time) * (1.0 - beat_time / 0.2) * 0.55

            # Snare on beats 1, 3, 5, 7
            snare = 0.0
            if beat_num % 2 == 1 and beat_time < 0.25:
                noise = ((hash(int(t * 26000)) % 100) / 50.0 - 1.0) * 0.3
                tone = math.sin(2 * math.pi * 180 * beat_time) * 0.25
                snare = (noise + tone) * (1.0 - beat_time / 0.25) * 0.45

            # Hi-hat on 8th notes
            hat_time = (t % (beat_dur / 2.0)) / (beat_dur / 2.0)
            hat = 0.0
            if hat_time < 0.06:
                hat = ((hash(int(t * 38000)) % 100) / 50.0 - 1.0) * (1.0 - hat_time / 0.06) * 0.18

            # Synth Bassline
            chord_idx = (beat_num // 2) % len(bass_notes)
            bfreq = bass_notes[chord_idx]
            sub_t = t % (beat_dur / 2.0)
            bass = (math.sin(2 * math.pi * bfreq * t) + 0.35 * math.sin(4 * math.pi * bfreq * t)) * (1.0 - (sub_t / (beat_dur / 2.0)) * 0.4) * 0.28

            # Arpeggiated melody
            arp_notes = [220.0, 261.6, 329.6, 392.0, 440.0, 523.2, 659.2, 784.0]
            arp_step = int((t * 4.0) % len(arp_notes))
            afreq = arp_notes[arp_step]
            arp_t = (t % 0.25) / 0.25
            arp = math.sin(2 * math.pi * afreq * t) * (1.0 - arp_t) * 0.16

            mix = kick + snare + hat + bass + arp
            val = int(max(-32767, min(32767, mix * 26000)))
            frames.append(struct.pack('<hh', val, val))

        buf = io.BytesIO()
        w = wave.open(buf, 'wb')
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(self.sample_rate)
        w.writeframes(b''.join(frames))
        w.close()
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_channel:
            if self.music_enabled:
                if hasattr(self, 'music_sound'):
                    self.music_channel.play(self.music_sound, loops=-1)
            else:
                self.music_channel.stop()
        return self.music_enabled

    def toggle_sfx(self):
        self.enabled = not self.enabled
        return self.enabled

AUDIO = SoundEngine()


# =====================================================
# FAST GLOW & PRE-RENDER CACHE PIPELINE
# =====================================================

GLOW_CACHE = {}

def get_glow_texture(radius, color):
    key = (int(radius), color[0], color[1], color[2])
    if key in GLOW_CACHE:
        return GLOW_CACHE[key]

    r = max(4, int(radius))
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    cx, cy = r, r

    for step in range(r, 0, -2):
        frac = step / r
        alpha = int(120 * (1.0 - frac) * (1.0 - frac))
        if alpha > 0:
            pygame.draw.circle(surf, (*color, min(255, alpha)), (cx, cy), step)

    GLOW_CACHE[key] = surf
    return surf

def draw_glow(surface, x, y, radius, color, alpha_mult=1.0):
    if radius <= 1:
        return
    texture = get_glow_texture(radius, color)
    if alpha_mult < 0.99:
        temp = texture.copy()
        temp.set_alpha(int(255 * alpha_mult))
        surface.blit(temp, (int(x - radius), int(y - radius)), special_flags=pygame.BLEND_RGBA_ADD)
    else:
        surface.blit(texture, (int(x - radius), int(y - radius)), special_flags=pygame.BLEND_RGBA_ADD)


# =====================================================
# JUICE ENGINE: CAMERA SHAKE, HITSTOP & COMBAT TEXT
# =====================================================

shake_timer = 0
shake_intensity = 0.0
hitstop_timer = 0

def trigger_shake(intensity, duration):
    global shake_intensity, shake_timer
    shake_intensity = max(shake_intensity, intensity)
    shake_timer = max(shake_timer, duration)

def trigger_hitstop(frames):
    global hitstop_timer
    hitstop_timer = max(hitstop_timer, frames)

def get_shake_offset():
    if shake_timer <= 0:
        return 0, 0
    decay = shake_timer / 12.0
    p = shake_intensity * decay
    return int(random.uniform(-p, p)), int(random.uniform(-p, p))


class FloatingText:
    def __init__(self, x, y, text, color=WHITE, font=FONT, vy=-3.5, lifetime=45):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.font = font
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.y += self.vy
        self.vy *= 0.92
        self.lifetime -= 1

    def draw(self, surface):
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        txt_surf = self.font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        # Shadow
        shadow = self.font.render(self.text, True, BLACK)
        shadow.set_alpha(int(alpha * 0.7))
        surface.blit(shadow, (int(self.x - txt_surf.get_width() // 2 + 2), int(self.y + 2)))
        surface.blit(txt_surf, (int(self.x - txt_surf.get_width() // 2), int(self.y)))

    def is_dead(self):
        return self.lifetime <= 0


class ShockwaveRing:
    def __init__(self, x, y, color, max_radius=80, duration=22, width=4):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.timer = duration
        self.max_width = width

    def update(self):
        self.timer -= 1

    def draw(self, surface):
        if self.timer <= 0:
            return
        progress = 1.0 - (self.timer / self.duration)
        r = int(self.max_radius * progress)
        if r < 2:
            return
        alpha = int(255 * (1.0 - progress))
        w = max(1, int(self.max_width * (1.0 - progress * 0.6)))

        ring_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*self.color, min(255, alpha)), (r + 5, r + 5), r, w)
        surface.blit(ring_surf, (int(self.x - r - 5), int(self.y - r - 5)), special_flags=pygame.BLEND_RGBA_ADD)

    def is_dead(self):
        return self.timer <= 0


class GroundDecal:
    def __init__(self, x, y, width, color=(40, 20, 25), lifetime=180):
        self.x = x
        self.y = y
        self.width = width
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.lifetime -= 1

    def draw(self, surface):
        progress = self.lifetime / self.max_lifetime
        alpha = int(180 * progress)
        decal_surf = pygame.Surface((self.width * 2, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(decal_surf, (*self.color, alpha), (0, 0, self.width * 2, 16))
        surface.blit(decal_surf, (int(self.x - self.width), int(self.y - 8)))

    def is_dead(self):
        return self.lifetime <= 0


# =====================================================
# PARTICLES & GHOST AFTER-IMAGES
# =====================================================

class Particle:
    def __init__(self, x, y, color, size, lifetime, vx=0.0, vy=0.0, gravity=0.0, shape='circle'):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.size = float(size)
        self.orig_size = float(size)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.shape = shape
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.96
        self.vy *= 0.96
        self.angle += self.rot_speed
        self.lifetime -= 1
        self.size = max(0.5, self.orig_size * (self.lifetime / self.max_lifetime))

    def draw(self, surface):
        if self.lifetime <= 0 or self.size < 0.5:
            return
        r = max(1, int(self.size))
        if self.shape == 'circle':
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)
        elif self.shape == 'spark':
            ex = self.x - self.vx * 2.5
            ey = self.y - self.vy * 2.5
            pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), (int(ex), int(ey)), max(1, r // 2))

    def is_dead(self):
        return self.lifetime <= 0 or self.size < 0.5


class GhostTrail:
    """Fading after-image silhouette rendered during high-speed dashes."""
    def __init__(self, champion, color, lifetime=14):
        self.x = champion.x
        self.y = champion.y
        self.color = color
        self.direction = champion.direction
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.lifetime -= 1

    def draw(self, surface):
        alpha = int(160 * (self.lifetime / self.max_lifetime))
        if alpha <= 0:
            return
        surf = pygame.Surface((50, 90), pygame.SRCALPHA)
        cx, cy = 25, 45
        pygame.draw.circle(surf, (*self.color, alpha), (cx, cy - 20), 16)
        pygame.draw.rect(surf, (*self.color, alpha), (cx - 14, cy - 8, 28, 42), border_radius=8)
        surface.blit(surf, (int(self.x - cx), int(self.y - cy)), special_flags=pygame.BLEND_RGBA_ADD)

    def is_dead(self):
        return self.lifetime <= 0


# =====================================================
# ARENA STAGES (MULTI-LAYER DYNAMIC BACKGROUNDS)
# =====================================================

class ArenaStage:
    def __init__(self, stage_id):
        self.stage_id = stage_id
        self.time = 0.0
        self.lightning_flash = 0
        self.ambient_particles = []
        self.init_stage_data()

    def init_stage_data(self):
        if self.stage_id == 'fire':
            self.name = "CALDERA OF IGNIS"
            self.bg_color = (20, 10, 16)
            self.ground_color = (38, 20, 24)
            self.accent = (245, 70, 25)
        elif self.stage_id == 'water':
            self.name = "ABYSSAL SANCTUARY"
            self.bg_color = (8, 20, 42)
            self.ground_color = (18, 38, 64)
            self.accent = (30, 160, 245)
        elif self.stage_id == 'lightning':
            self.name = "TEMPEST PEAKS"
            self.bg_color = (16, 12, 36)
            self.ground_color = (28, 24, 48)
            self.accent = (150, 60, 255)
        else: # astral
            self.name = "ASTRAL VOID NEXUS"
            self.bg_color = (10, 10, 22)
            self.ground_color = (25, 25, 45)
            self.accent = (65, 230, 210)

        # Prepopulate ambient particles
        for _ in range(35):
            self.spawn_ambient(random.uniform(0, WIDTH), random.uniform(50, GROUND_Y))

    def spawn_ambient(self, x=None, y=None):
        px = random.uniform(0, WIDTH) if x is None else x
        py = random.uniform(GROUND_Y - 20, GROUND_Y + 10) if y is None else y

        if self.stage_id == 'fire':
            p = Particle(px, py, random.choice([(255, 90, 20), (255, 170, 30), (255, 220, 60)]),
                         random.uniform(2, 4), random.randint(45, 90),
                         vx=random.uniform(-0.6, 0.6), vy=random.uniform(-1.5, -0.6), shape='spark')
        elif self.stage_id == 'water':
            p = Particle(px, py, (120, 220, 255), random.uniform(2, 5), random.randint(50, 100),
                         vx=random.uniform(-0.4, 0.4), vy=random.uniform(-1.0, -0.4))
        elif self.stage_id == 'lightning':
            p = Particle(px, py if y is not None else 0, (180, 210, 255), random.uniform(1.5, 3), random.randint(25, 45),
                         vx=random.uniform(-2.5, -1.5), vy=random.uniform(9.0, 14.0), shape='spark')
        else:
            p = Particle(px, py, random.choice([(180, 140, 255), (100, 240, 255), (255, 255, 255)]),
                         random.uniform(1.5, 3.5), random.randint(60, 120),
                         vx=random.uniform(-0.3, 0.3), vy=random.uniform(-0.3, 0.3))
        self.ambient_particles.append(p)

    def update(self):
        self.time += 0.02
        if self.lightning_flash > 0:
            self.lightning_flash -= 1

        if self.stage_id == 'lightning' and random.random() < 0.008:
            self.lightning_flash = 8
            trigger_shake(5, 6)

        if len(self.ambient_particles) < 40:
            self.spawn_ambient()

        for p in self.ambient_particles[:]:
            p.update()
            if p.is_dead() or p.y < 30 or p.y > HEIGHT:
                self.ambient_particles.remove(p)

    def draw(self, surface):
        surface.fill(self.bg_color)

        # Lightning Flash effect
        if self.lightning_flash > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill((210, 225, 255))
            flash_surf.set_alpha(int(90 * (self.lightning_flash / 8.0)))
            surface.blit(flash_surf, (0, 0))

        # Dynamic Stage Art
        t = self.time
        if self.stage_id == 'fire':
            # Jagged volcanic mountains in background
            pts = [(0, GROUND_Y), (0, 320), (220, 240), (450, 360), (700, 210), (950, 330), (WIDTH, 260), (WIDTH, GROUND_Y)]
            pygame.draw.polygon(surface, (30, 16, 22), pts)
            # Lava river flowing at ground
            for x in range(0, WIDTH, 30):
                wave_y = GROUND_Y - 4 + math.sin(t * 3 + x * 0.05) * 5
                pygame.draw.circle(surface, (255, 110, 25), (x, int(wave_y)), 12)
            draw_glow(surface, WIDTH // 2, GROUND_Y, 280, (255, 80, 20), 0.35)

        elif self.stage_id == 'water':
            # Underwater caustics / light shafts
            for i in range(7):
                shaft_x = 120 + i * 160 + math.sin(t + i) * 40
                pts = [(shaft_x - 35, 0), (shaft_x + 35, 0), (shaft_x + 95, GROUND_Y), (shaft_x - 15, GROUND_Y)]
                shaft_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(shaft_surf, (80, 200, 255, 22), pts)
                surface.blit(shaft_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            # Coral spires
            for cx in [160, 420, 850, 1050]:
                pygame.draw.rect(surface, (14, 30, 52), (cx - 24, 280, 48, GROUND_Y - 280), border_radius=12)

        elif self.stage_id == 'lightning':
            # Storm clouds
            for i in range(8):
                cx = i * 180 - 40
                cy = 70 + math.sin(t * 2 + i) * 15
                pygame.draw.circle(surface, (30, 24, 55), (int(cx), int(cy)), 110)
            # Distant spire towers
            for tx in [250, 600, 950]:
                pygame.draw.rect(surface, (22, 18, 42), (tx - 18, 200, 36, GROUND_Y - 200))
                pygame.draw.polygon(surface, (35, 30, 60), [(tx - 28, 200), (tx + 28, 200), (tx, 140)])

        else: # Astral
            # Nebula glowing dust
            draw_glow(surface, 350, 240, 220, (140, 50, 240), 0.3)
            draw_glow(surface, 850, 280, 240, (30, 190, 230), 0.3)
            # Ancient celestial clockwork rings
            ring_cx, ring_cy = WIDTH // 2, 280
            for r, spd in [(140, 0.4), (200, -0.25), (280, 0.15)]:
                ring_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (160, 220, 255, 35), (r + 5, r + 5), r, 2)
                # Ticks on ring
                for k in range(12):
                    ang = t * spd + k * (math.tau / 12)
                    tx1 = r + 5 + math.cos(ang) * (r - 6)
                    ty1 = r + 5 + math.sin(ang) * (r - 6)
                    tx2 = r + 5 + math.cos(ang) * (r + 4)
                    ty2 = r + 5 + math.sin(ang) * (r + 4)
                    pygame.draw.line(ring_surf, (200, 240, 255, 60), (tx1, ty1), (tx2, ty2), 2)
                surface.blit(ring_surf, (ring_cx - r - 5, ring_cy - r - 5))

        # Ambient Weather Particles
        for p in self.ambient_particles:
            p.draw(surface)

        # Foreground Arena Ground
        pygame.draw.rect(surface, self.ground_color, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(surface, self.accent, (0, GROUND_Y), (WIDTH, GROUND_Y), 4)

        # Ground geometric runic line accents
        for x in range(0, WIDTH, 60):
            pygame.draw.line(surface, (self.ground_color[0] + 15, self.ground_color[1] + 15, self.ground_color[2] + 20),
                             (x, GROUND_Y + 4), (x - 40, HEIGHT), 2)


# =====================================================
# PROJECTILE CLASS (TAILORED ELEMENTAL SPELLS)
# =====================================================

class Projectile:
    def __init__(self, x, y, direction, element_type, owner, vy=0.0, radius=9, damage=12, speed=13.0, is_parried=False):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.element_type = element_type
        self.owner = owner
        self.vy = vy
        self.radius = radius
        self.damage = damage
        self.speed = speed
        self.is_parried = is_parried

        self.timer = 110
        self.trail = []
        self.trail_max = 8
        self.anim_t = random.uniform(0, math.tau)

        elem = ELEMENT_DATA[element_type]
        self.main_color = elem['main']
        self.accent_color = elem['accent']
        self.highlight = elem['highlight']
        self.colors = elem['colors']

        self.rect = pygame.Rect(int(self.x - radius), int(self.y - radius), radius * 2, radius * 2)

    def update(self, particles):
        self.anim_t += 0.25
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)

        self.x += self.direction * self.speed
        self.y += self.vy
        self.timer -= 1
        self.rect.center = (int(self.x), int(self.y))

        # Trail particle discharge
        if random.random() < 0.85:
            vx = -self.direction * random.uniform(0.5, 2.5)
            vy = random.uniform(-1.0, 1.0)
            col = GOLD if self.is_parried else random.choice(self.colors)
            particles.append(Particle(self.x, self.y, col, random.uniform(2, 5), 14, vx, vy, shape='spark'))

    def draw(self, surface):
        # Motion trail ribbon
        for i, (tx, ty) in enumerate(self.trail):
            frac = (i + 1) / float(len(self.trail) + 1)
            tr = max(1, int(self.radius * frac * 0.75))
            alpha = int(140 * frac)
            col = GOLD if self.is_parried else self.accent_color
            tsurf = pygame.Surface((tr * 2, tr * 2), pygame.SRCALPHA)
            pygame.draw.circle(tsurf, (*col, alpha), (tr, tr), tr)
            surface.blit(tsurf, (int(tx - tr), int(ty - tr)), special_flags=pygame.BLEND_RGBA_ADD)

        # Glow
        draw_glow(surface, self.x, self.y, self.radius * 2.8, GOLD if self.is_parried else self.main_color, 0.8)

        cx, cy = int(self.x), int(self.y)
        # Element specific projectile graphics
        if self.element_type == 'fire':
            pygame.draw.circle(surface, self.main_color, (cx, cy), self.radius)
            pygame.draw.circle(surface, self.highlight, (cx + self.direction * 2, cy), max(2, self.radius // 2))
            pygame.draw.circle(surface, WHITE, (cx + self.direction * 4, cy), max(1, self.radius // 3))
        elif self.element_type == 'water':
            # Water tear-drop lance
            pts = [(cx + self.direction * self.radius * 1.5, cy),
                   (cx - self.direction * self.radius, cy - self.radius * 0.8),
                   (cx - self.direction * self.radius * 0.4, cy),
                   (cx - self.direction * self.radius, cy + self.radius * 0.8)]
            pygame.draw.polygon(surface, self.accent_color, pts)
            pygame.draw.polygon(surface, WHITE, pts, 1)
        elif self.element_type == 'earth':
            # Jagged faceted rotating rock
            pts = []
            for k in range(6):
                ang = self.anim_t + k * (math.tau / 6)
                rad = self.radius * (0.8 + 0.3 * math.sin(k * 2.1))
                pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
            pygame.draw.polygon(surface, self.main_color, pts)
            pygame.draw.polygon(surface, self.highlight, pts, 2)
        elif self.element_type == 'lightning':
            # Real-time procedural electric spark fork
            pts = [(cx - self.direction * self.radius * 1.5, cy)]
            for s in range(4):
                px = cx - self.direction * self.radius * (1.0 - s * 0.6)
                py = cy + random.uniform(-self.radius * 0.8, self.radius * 0.8)
                pts.append((px, py))
            pts.append((cx + self.direction * self.radius * 1.5, cy))
            pygame.draw.lines(surface, self.highlight, False, pts, 3)
            pygame.draw.circle(surface, WHITE, (cx, cy), max(2, self.radius // 2))
        else: # wind
            # Crescent sonic blade
            blade_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            bx, by = self.radius * 1.5, self.radius * 1.5
            pygame.draw.arc(blade_surf, (*self.highlight, 240), (bx - self.radius, by - self.radius, self.radius * 2, self.radius * 2),
                            -math.pi / 2, math.pi / 2, max(2, self.radius // 2))
            if self.direction < 0:
                blade_surf = pygame.transform.flip(blade_surf, True, False)
            surface.blit(blade_surf, (cx - bx, cy - by), special_flags=pygame.BLEND_RGBA_ADD)

    def is_finished(self):
        return (self.timer <= 0 or self.x < -100 or self.x > WIDTH + 100 or self.y < -50 or self.y > HEIGHT + 50)


# =====================================================
# CHARGED BEAM CLASS (HEAVY ELEMENTAL CANNON)
# =====================================================

class Beam:
    def __init__(self, player):
        self.player = player
        self.owner = player
        self.element_type = player.element_type
        self.direction = player.direction
        self.x, self.y = player.get_hand_position()

        self.length = 820
        self.max_width = 46
        self.min_width = 12
        self.timer = 32
        self.max_timer = self.timer
        self.damage = 16
        self.hit_targets = set()

        self.clash_limit = None
        self.clashing = False
        self.anim_time = 0.0

        elem = ELEMENT_DATA[self.element_type]
        self.main_color = elem['main']
        self.accent_color = elem['accent']
        self.highlight = elem['highlight']
        self.colors = elem['colors']

        self.rect = pygame.Rect(int(self.x), int(self.y - self.max_width // 2), self.length, self.max_width)
        if self.direction < 0:
            self.rect.left = int(self.x - self.length)

    def update(self, particles):
        if self.timer <= 0:
            return
        self.anim_time += 0.35
        self.timer -= 1
        self.x, self.y = self.player.get_hand_position()

        live_len = self.get_live_length()
        self.rect.width = int(live_len)
        self.rect.height = self.max_width
        self.rect.centery = int(self.y)

        if self.direction >= 0:
            self.rect.left = int(self.x)
        else:
            self.rect.right = int(self.x)

        # Energy spray particles along the beam
        for _ in range(3):
            dist = random.uniform(20, live_len)
            px = self.x + self.direction * dist
            py = self.y + random.uniform(-self.max_width * 0.45, self.max_width * 0.45)
            particles.append(Particle(px, py, random.choice(self.colors), random.uniform(2, 5), 14,
                                      vx=self.direction * random.uniform(2, 6), vy=random.uniform(-1.5, 1.5), shape='spark'))

    def get_live_length(self):
        if self.clash_limit is None:
            return self.length
        return max(10.0, abs(self.clash_limit - self.x))

    def get_live_rect(self):
        live_len = self.get_live_length()
        r = pygame.Rect(0, int(self.y - self.max_width // 2), int(live_len), self.max_width)
        if self.direction >= 0:
            r.left = int(self.x)
        else:
            r.right = int(self.x)
        return r

    def draw(self, surface):
        if self.timer <= 0:
            return
        progress = self.timer / float(self.max_timer)
        fade = min(1.0, (1.0 - progress) * 4.5 + 0.2)
        cur_width = max(self.min_width, int(self.max_width * fade))

        start_x = self.x
        end_x = start_x + self.direction * self.get_live_length()
        cy = int(self.y)
        beam_span = abs(end_x - start_x)

        if beam_span < 4:
            return

        # Radial Bloom Glow
        draw_glow(surface, (start_x + end_x) / 2.0, cy, cur_width * 2.2, self.main_color, 0.7 * fade)

        # Muzzle Flare Rings
        time_alive = self.max_timer - self.timer
        if time_alive < 12:
            flare_size = cur_width * (2.2 - time_alive * 0.1)
            pygame.draw.circle(surface, self.highlight, (int(start_x), cy), max(2, int(flare_size)), 3)
            pygame.draw.circle(surface, WHITE, (int(start_x), cy), max(1, int(flare_size * 0.5)))

        # Helical Spiral Energy Rings around beam core
        num_rings = max(2, int(beam_span / 26))
        for i in range(num_rings):
            t = i / float(num_rings)
            rx = start_x + self.direction * t * beam_span
            phase = (self.anim_time * 4 - i * 0.8) % math.tau
            ring_h = int(cur_width * (0.6 + 0.4 * math.sin(phase)))
            ring_w = max(3, int(cur_width * 0.28))
            pygame.draw.ellipse(surface, self.colors[i % len(self.colors)],
                                (int(rx - ring_w // 2), int(cy - ring_h // 2), ring_w, ring_h))

        # Main Laser Core
        pygame.draw.line(surface, self.main_color, (start_x, cy), (end_x, cy), max(3, cur_width // 2))
        pygame.draw.line(surface, self.highlight, (start_x, cy), (end_x, cy), max(2, cur_width // 4))
        pygame.draw.line(surface, WHITE, (start_x, cy), (end_x, cy), max(1, cur_width // 7))

    def is_finished(self):
        return self.timer <= 0


# =====================================================
# OVERDRIVE ULTIMATE ATTACK CLASS
# =====================================================

class UltimateSpell:
    def __init__(self, owner, opponent):
        self.owner = owner
        self.opponent = opponent
        self.element_type = owner.element_type
        self.elem_data = ELEMENT_DATA[self.element_type]
        self.timer = 130
        self.max_timer = 130
        self.damage = 26
        self.hit_applied = False
        self.sub_projectiles = []

        # Trigger cinema slowdown & sound
        AUDIO.play('ultimate')
        trigger_shake(16, 24)
        trigger_hitstop(18)

    def update(self, particles, shockwaves, decals):
        self.timer -= 1
        t_prog = 1.0 - (self.timer / float(self.max_timer))

        # Cinema Impact Frame at 40% progress
        if not self.hit_applied and self.timer <= 80:
            self.hit_applied = True
            mult = get_type_multiplier(self.element_type, self.opponent.element_type)
            final_dmg = int(self.damage * mult)
            self.opponent.take_damage(final_dmg, self.owner.direction)
            shockwaves.append(ShockwaveRing(self.opponent.x, self.opponent.y, self.elem_data['highlight'], 220, 35, 8))
            decals.append(GroundDecal(self.opponent.x, GROUND_Y, 90, self.elem_data['main'], 240))
            trigger_shake(20, 20)
            AUDIO.play('ko')

        # Element-specific ultimate particle manifestations
        if self.element_type == 'fire':
            # Falling meteorites
            for _ in range(4):
                mx = random.uniform(50, WIDTH - 50)
                particles.append(Particle(mx, 0, random.choice(self.elem_data['colors']), random.uniform(4, 9), 30,
                                          vx=random.uniform(-1, 1), vy=random.uniform(14, 22), shape='spark'))
        elif self.element_type == 'water':
            # Surging tidal geysers
            for _ in range(5):
                gx = random.uniform(60, WIDTH - 60)
                particles.append(Particle(gx, GROUND_Y, random.choice(self.elem_data['colors']), random.uniform(5, 10), 35,
                                          vx=random.uniform(-2, 2), vy=random.uniform(-18, -10)))
        elif self.element_type == 'earth':
            # Seismic rock eruptions
            for _ in range(4):
                ex = random.uniform(100, WIDTH - 100)
                particles.append(Particle(ex, GROUND_Y, random.choice(self.elem_data['colors']), random.uniform(6, 12), 40,
                                          vx=random.uniform(-4, 4), vy=random.uniform(-16, -8), gravity=0.5))
        elif self.element_type == 'lightning':
            # Cascading thunderbolts
            if random.random() < 0.4:
                lx = random.uniform(100, WIDTH - 100)
                shockwaves.append(ShockwaveRing(lx, GROUND_Y - 20, (180, 240, 255), 140, 18, 5))
                trigger_shake(8, 6)
        else: # wind
            # Colossal twisters
            for _ in range(6):
                wx = random.uniform(100, WIDTH - 100)
                particles.append(Particle(wx, random.uniform(100, GROUND_Y), random.choice(self.elem_data['colors']),
                                          random.uniform(4, 8), 30, vx=random.uniform(-8, 8), vy=random.uniform(-5, 5)))

    def draw(self, surface):
        if self.timer > 85:
            # Banner intro
            banner_surf = pygame.Surface((WIDTH, 110), pygame.SRCALPHA)
            banner_surf.fill((*self.elem_data['dark'], 210))
            surface.blit(banner_surf, (0, 180))

            title = HUGE_FONT.render(f"OVERDRIVE: {self.elem_data['ult_name']}", True, self.elem_data['highlight'])
            sub = FONT.render(f"Unleashed by {self.elem_data['name']} - {self.elem_data['title']}", True, WHITE)
            surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 195))
            surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 255))

    def is_finished(self):
        return self.timer <= 0


# =====================================================
# BEAM-VS-BEAM CLASH SYSTEM & STRUGGLE ENGINE
# =====================================================

class BeamClashManager:
    def __init__(self):
        self.active = False
        self.beam_a = None
        self.beam_b = None
        self.contact_x = WIDTH // 2
        self.clash_y = GROUND_Y - 100
        self.struggle_balance = 0.0  # -1.0 (P1 winning) to +1.0 (P2 winning)
        self.duration = 0

    def start_clash(self, b_a, b_b):
        self.active = True
        self.beam_a = b_a
        self.beam_b = b_b
        self.contact_x = (b_a.x + b_b.x) / 2.0
        self.clash_y = (b_a.y + b_b.y) / 2.0
        self.struggle_balance = 0.0
        self.duration = 90
        AUDIO.play('clash')

    def push(self, delta):
        self.struggle_balance = max(-1.0, min(1.0, self.struggle_balance + delta))

    def update(self, particles, shockwaves, floating_texts):
        if not self.active:
            return

        self.duration -= 1
        if self.beam_a.is_finished() or self.beam_b.is_finished() or self.duration <= 0 or abs(self.struggle_balance) >= 0.95:
            # Resolve clash finale!
            self.resolve_breakthrough(particles, shockwaves, floating_texts)
            return

        # Update contact point based on balance
        span = abs(self.beam_b.x - self.beam_a.x)
        self.contact_x = self.beam_a.x + self.beam_a.direction * (span * 0.5 + self.struggle_balance * (span * 0.4))
        self.clash_y = (self.beam_a.y + self.beam_b.y) / 2.0

        self.beam_a.clash_limit = self.contact_x
        self.beam_b.clash_limit = self.contact_x
        self.beam_a.clashing = True
        self.beam_b.clashing = True

        trigger_shake(5, 4)
        if random.random() < 0.6:
            AUDIO.play('clash')
            for _ in range(5):
                col = random.choice(self.beam_a.colors + self.beam_b.colors)
                particles.append(Particle(self.contact_x, self.clash_y, col, random.uniform(3, 7), 16,
                                          vx=random.uniform(-6, 6), vy=random.uniform(-6, 6), shape='spark'))

    def resolve_breakthrough(self, particles, shockwaves, floating_texts):
        self.active = False
        winner = self.beam_a if self.struggle_balance > 0 else self.beam_b
        loser = self.beam_b if self.struggle_balance > 0 else self.beam_a

        shockwaves.append(ShockwaveRing(self.contact_x, self.clash_y, winner.highlight, 180, 25, 7))
        floating_texts.append(FloatingText(self.contact_x, self.clash_y - 40, "⚡ CLASH BREAKTHROUGH! ⚡", GOLD, HEADER_FONT))
        trigger_shake(15, 16)
        trigger_hitstop(10)
        AUDIO.play('hit')

        loser.timer = 0  # Destroy loser beam
        winner.clash_limit = None  # Winner beam surges across screen
        winner.damage = int(winner.damage * 1.25)

    def draw(self, surface):
        if not self.active:
            return

        # Central Starburst
        cx, cy = int(self.contact_x), int(self.clash_y)
        draw_glow(surface, cx, cy, 75, WHITE, 0.9)
        draw_glow(surface, cx, cy, 120, self.beam_a.main_color, 0.6)

        # Clash Struggle UI Bar
        bar_w = 320
        bar_h = 24
        bx = WIDTH // 2 - bar_w // 2
        by = 130

        pygame.draw.rect(surface, (20, 24, 38), (bx - 4, by - 4, bar_w + 8, bar_h + 8), border_radius=8)
        pygame.draw.rect(surface, (70, 85, 120), (bx - 2, by - 2, bar_w + 4, bar_h + 4), 2, border_radius=8)

        # Center split indicator
        center_x = bx + bar_w // 2
        split_x = int(center_x + self.struggle_balance * (bar_w // 2 - 10))

        # P1 side
        pygame.draw.rect(surface, self.beam_a.main_color, (bx, by, split_x - bx, bar_h), border_radius=6)
        # P2 side
        pygame.draw.rect(surface, self.beam_b.main_color, (split_x, by, bx + bar_w - split_x, bar_h), border_radius=6)

        # Center clash pin
        pygame.draw.circle(surface, WHITE, (split_x, by + bar_h // 2), 10)
        pygame.draw.circle(surface, GOLD, (split_x, by + bar_h // 2), 6)

        hint = SMALL_FONT.render("⚡ BEAM STRUGGLE! MASH ATTACK! ⚡", True, GOLD)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, by - 22))


# =====================================================
# CHAMPION / PLAYER CLASS (HIGH GRAPHICS PROCEDURAL AVATAR)
# =====================================================

class Champion:
    def __init__(self, x, y, element_type, is_player_one, is_cpu=False, cpu_difficulty='normal'):
        self.x = float(x)
        self.y = float(y)
        self.element_type = element_type
        self.is_player_one = is_player_one
        self.is_cpu = is_cpu
        self.cpu_difficulty = cpu_difficulty

        elem = ELEMENT_DATA[element_type]
        self.name = elem['name']
        self.color = elem['main']
        self.accent = elem['accent']
        self.highlight = elem['highlight']
        self.dark = elem['dark']
        self.colors = elem['colors']

        # Health & Stats
        self.max_hp = 160
        self.hp = 160
        self.display_hp = 160.0
        self.damage_lag_hp = 160.0

        # Stamina & Burst (Super Gauge)
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.stamina_regen = 0.32
        self.burst = 0.0  # 0 to 100%

        # Kinematics & Physics
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 6.0
        self.is_grounded = True
        self.direction = 1 if is_player_one else -1

        # Dash Mechanics
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.is_invulnerable = False

        # Shield & Parry
        self.shield_timer = 0
        self.shield_cooldown = 0
        self.parry_window = 0  # 6-frame window for Perfect Parry

        # Attacks & Charging
        self.charging = False
        self.charge_time = 0
        self.charge_threshold = 42
        self.attack_timer = 0
        self.attack_flash = 0
        self.barrage_queue = 0
        self.barrage_cooldown = 0

        # Cape & Visual Nodes
        self.cape_nodes = [[self.x, self.y] for _ in range(5)]
        self.anim_t = random.uniform(0, math.tau)
        self.hit_flash = 0
        self.squash_amount = 0.0
        self.walk_phase = 0.0
        self.bob_amp = 0.0
        self.lean = 0.0

        # Combat statistics
        self.hits_landed = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.parries_landed = 0
        self.total_damage_dealt = 0

        # CPU AI state
        self.ai_timer = random.randint(10, 30)
        self.ai_action = 'idle'

        self.rect = pygame.Rect(int(x - 22), int(y - 50), 44, 85)

    def jump(self):
        if self.is_grounded and self.stamina >= 10.0:
            self.vy = -14.5
            self.is_grounded = False
            self.squash_amount = 0.35
            self.stamina -= 8.0
            AUDIO.play('move')

    def dash(self, ghosts):
        if self.dash_cooldown <= 0 and self.stamina >= 18.0:
            self.stamina -= 18.0
            self.dash_timer = 9
            self.dash_cooldown = 45
            self.is_invulnerable = True
            self.vx = self.direction * 19.0
            self.squash_amount = 0.45
            AUDIO.play('dash')
            ghosts.append(GhostTrail(self, self.color))

    def trigger_shield(self):
        shield_cost = 18.0
        if self.shield_cooldown <= 0 and self.shield_timer <= 0 and self.stamina >= shield_cost:
            self.stamina -= shield_cost
            self.shield_timer = 32
            self.shield_cooldown = 110
            self.parry_window = 7  # 7-frame Perfect Parry window!
            self.squash_amount = -0.3
            AUDIO.play('shield')

    def trigger_barrage(self):
        cost = 28.0
        if self.barrage_cooldown <= 0 and self.barrage_queue == 0 and self.stamina >= cost:
            self.stamina -= cost
            self.barrage_queue = 5
            self.barrage_cooldown = 130
            AUDIO.play('shoot')

    def update_physics(self, ghosts, particles):
        self.anim_t += 0.12

        # Horizontal kinematics
        self.x += self.vx
        self.vx *= 0.88
        if abs(self.vx) < 0.1:
            self.vx = 0.0

        # Dash decay & ghost spawning
        if self.dash_timer > 0:
            self.dash_timer -= 1
            if self.dash_timer % 3 == 0:
                ghosts.append(GhostTrail(self, self.highlight))
            if self.dash_timer <= 0:
                self.is_invulnerable = False

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # Vertical gravity & Jump
        self.y += self.vy
        self.vy += 0.72  # Gravity

        if self.y >= GROUND_Y - 45:
            if not self.is_grounded:
                self.squash_amount = -0.35  # Landing squash
                for _ in range(4):
                    particles.append(Particle(self.x, GROUND_Y, (90, 110, 140), random.uniform(2, 4), 12,
                                              vx=random.uniform(-2, 2), vy=random.uniform(-1, 0)))
            self.y = GROUND_Y - 45
            self.vy = 0.0
            self.is_grounded = True
        else:
            self.is_grounded = False

        # Arena boundaries
        half_boundary = WIDTH // 2 - 40 if not self.is_cpu and False else WIDTH - 60
        self.x = max(60, min(WIDTH - 60, self.x))
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Smooth HP animations
        self.display_hp += (self.hp - self.display_hp) * 0.15
        self.damage_lag_hp += (self.hp - self.damage_lag_hp) * 0.035

        # Stamina regeneration
        if not self.charging and self.shield_timer <= 0:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)

        # Cooldown ticks
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.parry_window > 0:
            self.parry_window -= 1
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.barrage_cooldown > 0:
            self.barrage_cooldown -= 1

        # Combo reset timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0

        # Squash & Stretch relaxation
        self.squash_amount *= 0.82

        # Dynamic Cape Physics simulation
        anchor_x = self.x - self.direction * 12
        anchor_y = self.y - 20
        self.cape_nodes[0] = [anchor_x, anchor_y]
        for i in range(1, len(self.cape_nodes)):
            target_x = self.cape_nodes[i - 1][0] - self.direction * 10 - self.vx * 1.5
            target_y = self.cape_nodes[i - 1][1] + 12 + math.sin(self.anim_t * 2.5 + i) * 3
            self.cape_nodes[i][0] += (target_x - self.cape_nodes[i][0]) * 0.45
            self.cape_nodes[i][1] += (target_y - self.cape_nodes[i][1]) * 0.45

    def update_attack_state(self, projectiles, particles):
        # Barrage burst firing
        if self.barrage_queue > 0:
            if self.attack_timer <= 0:
                self.attack_timer = 5
                self.barrage_queue -= 1
                hx, hy = self.get_hand_position()
                spread_vy = random.uniform(-2.5, 2.5)
                projectiles.append(Projectile(hx, hy, self.direction, self.element_type, self,
                                              vy=spread_vy, radius=7, damage=3, speed=14.0))
                AUDIO.play('shoot')

        # Charging particles & hum
        if self.charging:
            self.charge_time += 1
            hx, hy = self.get_hand_position()
            prog = min(1.0, self.charge_time / float(self.charge_threshold))
            for _ in range(2):
                ang = random.uniform(0, math.tau)
                dist = random.uniform(22, 45 + prog * 20)
                px = hx + math.cos(ang) * dist
                py = hy + math.sin(ang) * dist
                vx = (hx - px) * 0.1
                vy = (hy - py) * 0.1
                particles.append(Particle(px, py, random.choice(self.colors), random.uniform(2, 6), 14, vx, vy, shape='spark'))

    def release_attack(self):
        charged = self.charge_time >= self.charge_threshold
        self.charging = False
        self.charge_time = 0

        cost = 25.0 if charged else 14.0
        if self.stamina >= cost:
            self.stamina -= cost
            self.attack_timer = 18
            self.squash_amount = 0.45 if charged else 0.25

            if charged:
                self.vx = -self.direction * 12.0  # Recoil
                AUDIO.play('beam')
                return Beam(self)
            else:
                hx, hy = self.get_hand_position()
                AUDIO.play('shoot')
                return Projectile(hx, hy, self.direction, self.element_type, self,
                                  radius=10, damage=6, speed=13.0)
        return None

    def trigger_ultimate(self, opponent):
        if self.burst >= 100.0:
            self.burst = 0.0
            return UltimateSpell(self, opponent)
        return None

    def take_damage(self, damage, attacker_direction=0):
        if self.is_invulnerable:
            return False

        if self.shield_timer > 0:
            # Blocked with shield
            damage = int(damage * 0.3)
            self.stamina = max(0.0, self.stamina - 15.0)
            AUDIO.play('hit')
            trigger_shake(4, 5)
            return False

        self.hp = max(0, self.hp - damage)
        self.hit_flash = 12
        self.squash_amount = -0.4
        self.vx += attacker_direction * 7.5
        self.burst = min(100.0, self.burst + damage * 0.8)  # Gain burst on damage taken
        AUDIO.play('hit')
        trigger_shake(min(16, 5 + damage * 0.4), 10)
        trigger_hitstop(6 if damage >= 20 else 3)
        return True

    def get_hand_position(self):
        sway = math.sin(self.anim_t * 2.5) * 3
        hx = self.x + self.direction * (24 if self.attack_timer > 0 else 16)
        hy = self.y - 12 + sway
        return hx, hy

    def update_cpu_ai(self, opponent, projectiles, beams, ghosts):
        if not self.is_cpu:
            return

        self.ai_timer -= 1
        dist_x = abs(opponent.x - self.x)

        # Danger detection: Incoming projectiles/beams
        threat = None
        for p in projectiles:
            if p.owner is not self and math.copysign(1, p.direction) == math.copysign(1, self.x - p.x):
                if abs(p.x - self.x) < 280:
                    threat = p
                    break

        if self.cpu_difficulty == 'grandmaster':
            # Grandmaster attempts Perfect Parries and aggressive dashing
            if threat and abs(threat.x - self.x) < 140:
                if self.shield_cooldown <= 0 and self.stamina >= 20:
                    self.trigger_shield()
                elif self.dash_cooldown <= 0:
                    self.dash(ghosts)

        elif self.cpu_difficulty == 'normal':
            if threat and abs(threat.x - self.x) < 160:
                if random.random() < 0.65 and self.shield_cooldown <= 0:
                    self.trigger_shield()
                elif random.random() < 0.35:
                    self.jump()

        # Decision making on timer
        if self.ai_timer <= 0:
            self.ai_timer = random.randint(15, 35)
            # Distance management
            if dist_x > 450:
                self.vx = self.direction * self.speed * 0.9
                if random.random() < 0.35:
                    self.charging = True
                    self.charge_time = 0
            elif dist_x < 180:
                self.vx = -self.direction * self.speed * 0.8
                if random.random() < 0.4:
                    self.trigger_barrage()
            else:
                if random.random() < 0.4:
                    self.jump()

            # Unleash Ultimate when full
            if self.burst >= 100.0:
                self.ai_action = 'ultimate'

        # Attack execution while charging
        if self.charging:
            if self.charge_time >= self.charge_threshold:
                attack = self.release_attack()
                if isinstance(attack, Beam):
                    beams.append(attack)
                elif isinstance(attack, Projectile):
                    projectiles.append(attack)
            elif threat and dist_x < 200:
                # Cancel or early release
                attack = self.release_attack()
                if attack:
                    projectiles.append(attack)

    def draw(self, surface, opponent):
        # Look towards opponent
        if opponent:
            self.direction = 1 if opponent.x > self.x else -1

        t = self.anim_t
        breathe = math.sin(t * 2.0) * 2.5
        s = self.squash_amount
        upper_y = self.y + breathe
        shoulder_y = upper_y - 18
        head_y = upper_y - 48

        # Ground Dynamic Shadow
        shadow_scale = max(0.4, 1.0 - (GROUND_Y - 45 - self.y) / 250.0)
        shadow_surf = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, int(110 * shadow_scale)), (0, 0, 60 * shadow_scale, 16 * shadow_scale))
        surface.blit(shadow_surf, (int(self.x - 30 * shadow_scale), GROUND_Y - 8))

        # 1. Flowing Segmented Cloth Cape
        if len(self.cape_nodes) >= 4:
            pts = [(self.cape_nodes[0][0], self.cape_nodes[0][1])]
            for node in self.cape_nodes:
                pts.append((node[0], node[1]))
            # Backside of cape
            for node in reversed(self.cape_nodes):
                pts.append((node[0] - self.direction * 12, node[1] + 4))
            pygame.draw.polygon(surface, self.dark, pts)
            pygame.draw.lines(surface, self.accent, False, pts[:len(self.cape_nodes)], 2)

        # 2. Charging Magic Circle Runes
        if self.charging:
            prog = min(1.0, self.charge_time / float(self.charge_threshold))
            r = 30 + prog * 28
            ring_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
            rcx, rcy = r + 5, r + 5
            pygame.draw.circle(ring_surf, (*self.highlight, int(180 * prog)), (rcx, rcy), int(r), 2)
            # Spinning geometric inscribed triangle
            for k in range(3):
                ang = t * 3.5 + k * (math.tau / 3)
                p1 = (rcx + math.cos(ang) * r, rcy + math.sin(ang) * r)
                p2 = (rcx + math.cos(ang + math.tau / 3) * r, rcy + math.sin(ang + math.tau / 3) * r)
                pygame.draw.line(ring_surf, (*self.color, int(140 * prog)), p1, p2, 1)
            surface.blit(ring_surf, (int(self.x - rcx), int(GROUND_Y - 14)), special_flags=pygame.BLEND_RGBA_ADD)

        # 3. Holographic Shield Dome
        if self.shield_timer > 0:
            sh_r = 54
            sh_surf = pygame.Surface((sh_r * 2 + 10, sh_r * 2 + 10), pygame.SRCALPHA)
            scx, scy = sh_r + 5, sh_r + 5
            # Perfect parry bright golden tint during parry window
            sh_col = GOLD if self.parry_window > 0 else (120, 220, 255)
            pygame.draw.circle(sh_surf, (*sh_col, 80), (scx, scy), sh_r, 4)
            # Hexagonal pattern
            for k in range(6):
                ang = t * 1.5 + k * (math.tau / 6)
                px = scx + math.cos(ang) * sh_r
                py = scy + math.sin(ang) * sh_r
                pygame.draw.line(sh_surf, (*sh_col, 160), (scx, scy), (px, py), 1)
            surface.blit(sh_surf, (int(self.x - scx), int(upper_y - scy)), special_flags=pygame.BLEND_RGBA_ADD)

        # 4. Body & Armor
        main_c = WHITE if (self.hit_flash > 0 and (self.hit_flash // 2) % 2 == 0) else self.color
        body_w = int(32 * (1.0 - s * 0.5))
        body_h = int(48 * (1.0 + s * 0.5))
        body_rect = pygame.Rect(int(self.x - body_w // 2), int(upper_y - 20), body_w, body_h)

        # Legs
        pygame.draw.rect(surface, BLACK, (int(self.x - 12), int(upper_y + 18), 9, 26), border_radius=4)
        pygame.draw.rect(surface, self.dark, (int(self.x - 10), int(upper_y + 19), 7, 24), border_radius=3)
        pygame.draw.rect(surface, BLACK, (int(self.x + 3), int(upper_y + 18), 9, 26), border_radius=4)
        pygame.draw.rect(surface, self.dark, (int(self.x + 5), int(upper_y + 19), 7, 24), border_radius=3)

        # Torso & Core
        pygame.draw.rect(surface, BLACK, (body_rect.x - 2, body_rect.y - 2, body_rect.width + 4, body_rect.height + 4), border_radius=10)
        pygame.draw.rect(surface, main_c, body_rect, border_radius=8)

        # Glowing Elemental Chest Core
        core_y = upper_y - 4
        pygame.draw.circle(surface, self.highlight, (int(self.x), int(core_y)), 7)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(core_y)), 3)
        draw_glow(surface, self.x, core_y, 16, self.highlight, 0.7)

        # Head & Visor
        pygame.draw.circle(surface, BLACK, (int(self.x), int(head_y)), 16)
        pygame.draw.circle(surface, main_c, (int(self.x), int(head_y)), 14)
        # Element Head Crest / Horns
        if self.element_type == 'fire':
            pygame.draw.polygon(surface, self.highlight, [(self.x - 6, head_y - 12), (self.x, head_y - 24), (self.x + 6, head_y - 12)])
        elif self.element_type == 'water':
            pygame.draw.polygon(surface, self.accent, [(self.x, head_y - 14), (self.x - self.direction * 14, head_y - 22), (self.x, head_y - 8)])
        elif self.element_type == 'earth':
            pygame.draw.rect(surface, self.highlight, (int(self.x - 8), int(head_y - 20), 16, 7), border_radius=2)
        elif self.element_type == 'lightning':
            pygame.draw.lines(surface, self.highlight, False, [(self.x - 8, head_y - 12), (self.x, head_y - 24), (self.x + 8, head_y - 14)], 3)
        else: # wind
            pygame.draw.arc(surface, self.highlight, (self.x - 12, head_y - 22, 24, 18), 0, math.pi, 3)

        # Glowing Visor / Eyes
        eye_x = int(self.x + self.direction * 6)
        eye_y = int(head_y)
        pygame.draw.circle(surface, self.highlight, (eye_x, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 2)

        # Arms & Casting Relic Hands
        hx, hy = self.get_hand_position()
        pygame.draw.line(surface, BLACK, (self.x, shoulder_y), (hx, hy), 8)
        pygame.draw.line(surface, self.highlight, (self.x, shoulder_y), (hx, hy), 5)
        pygame.draw.circle(surface, WHITE, (int(hx), int(hy)), 5)

        # 5. Orbiting Elemental Catalysts (3D Elliptical Orbits)
        for idx in range(3):
            orb_ang = t * 2.0 + idx * (math.tau / 3)
            orb_x = self.x + math.cos(orb_ang) * 32
            orb_y = upper_y - 10 + math.sin(orb_ang) * 12
            orb_z = math.sin(orb_ang)  # Depth
            orb_r = max(2, int(4 + orb_z * 2))
            draw_glow(surface, orb_x, orb_y, orb_r * 2.5, self.highlight, 0.5)
            pygame.draw.circle(surface, self.highlight, (int(orb_x), int(orb_y)), orb_r)
            pygame.draw.circle(surface, WHITE, (int(orb_x), int(orb_y)), max(1, orb_r // 2))


# =====================================================
# COMBAT RESOLUTION & PERFECT PARRY ENGINE
# =====================================================

def resolve_combat_interactions(projectiles, beams, champions, particles, shockwaves, floating_texts, clash_manager):
    # 1. Opposing Projectile collisions & Clashes
    destroyed_p = set()
    for i, p1 in enumerate(projectiles):
        if id(p1) in destroyed_p:
            continue
        for p2 in projectiles[i + 1:]:
            if id(p2) in destroyed_p or p1.owner is p2.owner:
                continue
            if p1.rect.colliderect(p2.rect):
                cx = (p1.x + p2.x) / 2
                cy = (p1.y + p2.y) / 2
                shockwaves.append(ShockwaveRing(cx, cy, WHITE, 50, 15, 3))
                floating_texts.append(FloatingText(cx, cy - 20, "CLASH!", GOLD, SMALL_FONT))
                trigger_shake(4, 5)
                AUDIO.play('clash')
                destroyed_p.add(id(p1))
                destroyed_p.add(id(p2))
                for _ in range(8):
                    particles.append(Particle(cx, cy, random.choice(p1.colors + p2.colors), random.uniform(3, 6), 14,
                                              vx=random.uniform(-4, 4), vy=random.uniform(-4, 4), shape='spark'))
                break

    if destroyed_p:
        projectiles[:] = [p for p in projectiles if id(p) not in destroyed_p]

    # 2. Beams shred incoming projectiles
    destroyed_p = set()
    for proj in projectiles:
        if id(proj) in destroyed_p:
            continue
        for beam in beams:
            if beam.owner is proj.owner:
                continue
            if proj.rect.colliderect(beam.get_live_rect()):
                shockwaves.append(ShockwaveRing(proj.x, proj.y, beam.highlight, 40, 12, 2))
                destroyed_p.add(id(proj))
                break
    if destroyed_p:
        projectiles[:] = [p for p in projectiles if id(p) not in destroyed_p]

    # 3. Beam vs Beam Clash Detection
    for i, b1 in enumerate(beams):
        for b2 in beams[i + 1:]:
            if b1.owner is b2.owner:
                continue
            if b1.get_live_rect().colliderect(b2.get_live_rect()) and not clash_manager.active:
                clash_manager.start_clash(b1, b2)

    # 4. Projectile impacts against Champions & PERFECT PARRY
    for proj in projectiles[:]:
        for champ in champions:
            if proj.owner is champ:
                continue
            if proj.rect.colliderect(champ.rect):
                # Check for PERFECT PARRY!
                if champ.parry_window > 0:
                    AUDIO.play('parry')
                    champ.parries_landed += 1
                    champ.stamina = min(champ.max_stamina, champ.stamina + 35.0)
                    champ.burst = min(100.0, champ.burst + 25.0)
                    shockwaves.append(ShockwaveRing(champ.x, champ.y, GOLD, 120, 25, 5))
                    floating_texts.append(FloatingText(champ.x, champ.y - 60, "PERFECT PARRY!", GOLD, HEADER_FONT))
                    trigger_shake(8, 8)
                    trigger_hitstop(5)

                    # Reverse projectile!
                    proj.direction = -proj.direction
                    proj.owner = champ
                    proj.speed *= 1.4
                    proj.damage = int(proj.damage * 1.3)
                    proj.is_parried = True
                    break

                # Standard Hit
                mult = get_type_multiplier(proj.element_type, champ.element_type)
                final_dmg = int(proj.damage * mult)
                if champ.take_damage(final_dmg, proj.direction):
                    proj.owner.total_damage_dealt += final_dmg
                    proj.owner.hits_landed += 1
                    proj.owner.combo_count += 1
                    proj.owner.combo_timer = 90
                    # Floating combat text
                    crit_txt = f"{final_dmg} CRIT!" if mult > 1.2 else f"{final_dmg}"
                    crit_col = CRIT_RED if mult > 1.2 else (GOLD if mult >= 1.0 else (170, 200, 255))
                    floating_texts.append(FloatingText(champ.x, champ.y - 35, crit_txt, crit_col, FONT))
                    if mult > 1.2:
                        floating_texts.append(FloatingText(champ.x, champ.y - 55, "SUPER EFFECTIVE!", GOLD, SMALL_FONT))

                for _ in range(8):
                    particles.append(Particle(proj.x, proj.y, random.choice(proj.colors), random.uniform(2, 5), 14,
                                              vx=random.uniform(-3, 3), vy=random.uniform(-3, 3), shape='spark'))
                projectiles.remove(proj)
                break

    # 5. Beam impacts against Champions
    for beam in beams:
        for champ in champions:
            if beam.owner is champ or champ in beam.hit_targets:
                continue
            if beam.get_live_rect().colliderect(champ.rect):
                beam.hit_targets.add(champ)
                mult = get_type_multiplier(beam.element_type, champ.element_type)
                final_dmg = int(beam.damage * mult)
                if champ.take_damage(final_dmg, beam.direction):
                    beam.owner.total_damage_dealt += final_dmg
                    beam.owner.hits_landed += 1
                    beam.owner.combo_count += 1
                    beam.owner.combo_timer = 90
                    crit_txt = f"{final_dmg} BEAM CRIT!" if mult > 1.2 else f"{final_dmg}"
                    floating_texts.append(FloatingText(champ.x, champ.y - 45, crit_txt, GOLD, HEADER_FONT))
                shockwaves.append(ShockwaveRing(champ.x, champ.y, beam.highlight, 90, 18, 4))


# =====================================================
# POLISHED BATTLE HUD & COMBAT UI
# =====================================================

def draw_battle_hud(surface, p1, p2, match_time, stage_name):
    # Top Bar Background Plate
    bar_plate = pygame.Surface((WIDTH, 110), pygame.SRCALPHA)
    pygame.draw.rect(bar_plate, (12, 16, 32, 220), (0, 0, WIDTH, 95))
    pygame.draw.line(bar_plate, (60, 80, 130, 180), (0, 95), (WIDTH, 95), 2)
    surface.blit(bar_plate, (0, 0))

    # Match Timer in Center
    secs = max(0, int(match_time))
    timer_surf = TITLE_FONT.render(f"{secs}", True, WHITE)
    surface.blit(timer_surf, (WIDTH // 2 - timer_surf.get_width() // 2, 10))

    # Clickable Menu button in battle
    mx, my = pygame.mouse.get_pos()
    hud_menu_btn = pygame.Rect(WIDTH // 2 - 48, 64, 96, 22)
    m_hover = hud_menu_btn.collidepoint(mx, my)
    pygame.draw.rect(surface, (45, 55, 85) if m_hover else (22, 28, 48), hud_menu_btn, border_radius=5)
    pygame.draw.rect(surface, GOLD if m_hover else (70, 90, 135), hud_menu_btn, 1, border_radius=5)
    m_txt = TINY_FONT.render("< MENU (ESC)", True, GOLD if m_hover else (190, 210, 240))
    surface.blit(m_txt, (hud_menu_btn.centerx - m_txt.get_width() // 2, hud_menu_btn.centery - m_txt.get_height() // 2))

    # Player 1 HUD (Left)
    draw_player_hud_card(surface, 40, 15, p1, is_p1=True)

    # Player 2 / CPU HUD (Right)
    draw_player_hud_card(surface, WIDTH - 470, 15, p2, is_p1=False)

    # Dynamic Combo Counter
    if p1.combo_count >= 2:
        combo_txt = HEADER_FONT.render(f"{p1.combo_count} HITS!", True, GOLD)
        surface.blit(combo_txt, (180, 115))
    if p2.combo_count >= 2:
        combo_txt = HEADER_FONT.render(f"{p2.combo_count} HITS!", True, GOLD)
        surface.blit(combo_txt, (WIDTH - 180 - combo_txt.get_width(), 115))


def draw_player_hud_card(surface, x, y, player, is_p1=True):
    width = 430
    elem = ELEMENT_DATA[player.element_type]

    # Avatar Badge Frame
    badge_x = x if is_p1 else (x + width - 68)
    pygame.draw.rect(surface, (20, 26, 48), (badge_x, y + 2, 64, 64), border_radius=12)
    pygame.draw.rect(surface, elem['main'], (badge_x, y + 2, 64, 64), 3, border_radius=12)
    elem_icon = HEADER_FONT.render(elem['name'][:2], True, elem['highlight'])
    surface.blit(elem_icon, (badge_x + 32 - elem_icon.get_width() // 2, y + 34 - elem_icon.get_height() // 2))

    bars_x = (x + 78) if is_p1 else x
    bars_w = 340

    # Name & Element Title
    p_tag = "P1" if is_p1 else ("CPU" if player.is_cpu else "P2")
    title_surf = FONT.render(f"{p_tag}: {elem['name']}", True, WHITE)
    surface.blit(title_surf, (bars_x, y - 2))

    hp_num = SMALL_FONT.render(f"{int(player.hp)} / {int(player.max_hp)}", True, (210, 230, 255))
    surface.blit(hp_num, (bars_x + bars_w - hp_num.get_width(), y - 2))

    # Health Bar (with dynamic red damage lag)
    bar_y = y + 22
    bar_h = 16
    pygame.draw.rect(surface, (45, 20, 30), (bars_x, bar_y, bars_w, bar_h), border_radius=5)

    lag_w = int(bars_w * max(0.0, player.damage_lag_hp) / player.max_hp)
    if lag_w > 0:
        pygame.draw.rect(surface, (220, 70, 70), (bars_x, bar_y, lag_w, bar_h), border_radius=5)

    hp_w = int(bars_w * max(0.0, player.display_hp) / player.max_hp)
    if hp_w > 0:
        pygame.draw.rect(surface, elem['main'], (bars_x, bar_y, hp_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, elem['highlight'], (bars_x, bar_y, hp_w, bar_h // 2), border_radius=4)
    pygame.draw.rect(surface, (180, 205, 240), (bars_x, bar_y, bars_w, bar_h), 2, border_radius=5)

    # Stamina Bar
    st_y = bar_y + bar_h + 4
    st_h = 8
    pygame.draw.rect(surface, (25, 30, 48), (bars_x, st_y, bars_w, st_h), border_radius=3)
    st_w = int(bars_w * max(0.0, player.stamina) / player.max_stamina)
    if st_w > 0:
        pygame.draw.rect(surface, (245, 210, 50), (bars_x, st_y, st_w, st_h), border_radius=3)

    # Burst Gauge (Overdrive Meter)
    burst_y = st_y + st_h + 4
    burst_h = 7
    pygame.draw.rect(surface, (30, 20, 45), (bars_x, burst_y, bars_w, burst_h), border_radius=3)
    b_w = int(bars_w * max(0.0, min(100.0, player.burst)) / 100.0)
    b_col = GOLD if player.burst >= 100.0 else (60, 180, 255)
    if b_w > 0:
        pygame.draw.rect(surface, b_col, (bars_x, burst_y, b_w, burst_h), border_radius=3)

    # Indicators: Shield Cooldown / Burst Ready
    if player.burst >= 100.0:
        over_txt = TINY_FONT.render("★ OVERDRIVE READY (Q) ★", True, GOLD)
        surface.blit(over_txt, (bars_x, burst_y + burst_h + 2))
    elif player.shield_cooldown > 0:
        cd_s = math.ceil(player.shield_cooldown / 60.0)
        cd_txt = TINY_FONT.render(f"Shield CD: {cd_s}s", True, (210, 160, 160))
        surface.blit(cd_txt, (bars_x, burst_y + burst_h + 2))


# =====================================================
# CHARACTER & STAGE SELECTION SCREEN
# =====================================================

class SelectionScreen:
    def __init__(self):
        self.p1_idx = 0
        self.p2_idx = 1
        self.stage_idx = 0
        self.stages = ['fire', 'water', 'lightning', 'astral']
        self.mode = 'VS_CPU'
        self.ai_difficulty = 'normal'
        self.difficulties = ['apprentice', 'normal', 'grandmaster']
        self.diff_idx = 1

        self.back_btn = pygame.Rect(40, 24, 160, 42)
        self.start_btn = pygame.Rect(WIDTH // 2 - 160, 610, 320, 52)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                AUDIO.play('move')
                return "BACK"

            # P1 element toggle: A / D
            elif event.key == pygame.K_a:
                self.p1_idx = (self.p1_idx - 1) % len(ELEMENT_LIST)
                AUDIO.play('move')
            elif event.key == pygame.K_d:
                self.p1_idx = (self.p1_idx + 1) % len(ELEMENT_LIST)
                AUDIO.play('move')

            # P2 element toggle: LEFT / RIGHT
            elif event.key == pygame.K_LEFT:
                self.p2_idx = (self.p2_idx - 1) % len(ELEMENT_LIST)
                AUDIO.play('move')
            elif event.key == pygame.K_RIGHT:
                self.p2_idx = (self.p2_idx + 1) % len(ELEMENT_LIST)
                AUDIO.play('move')

            # Stage toggle: TAB
            elif event.key == pygame.K_TAB:
                self.stage_idx = (self.stage_idx + 1) % len(self.stages)
                AUDIO.play('move')

            # Difficulty toggle: T
            elif event.key == pygame.K_t:
                self.diff_idx = (self.diff_idx + 1) % len(self.difficulties)
                self.ai_difficulty = self.difficulties[self.diff_idx]
                AUDIO.play('move')

            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                AUDIO.play('select')
                return "START"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.collidepoint(event.pos):
                AUDIO.play('move')
                return "BACK"
            if self.start_btn.collidepoint(event.pos):
                AUDIO.play('select')
                return "START"

        return None

    def draw(self, surface):
        surface.fill(DARK_BG)

        # Background decorative glow
        draw_glow(surface, 280, 320, 240, ELEMENT_DATA[ELEMENT_LIST[self.p1_idx]]['main'], 0.25)
        draw_glow(surface, 920, 320, 240, ELEMENT_DATA[ELEMENT_LIST[self.p2_idx]]['main'], 0.25)

        # Header Title
        title = HUGE_FONT.render("CHOOSE YOUR CHAMPION", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 25))

        sub = FONT.render(f"MODE: {self.mode.replace('_', ' ')}  |  STAGE: {self.stages[self.stage_idx].upper()} [TAB]  |  CPU: {self.ai_difficulty.upper()} [T]", True, GOLD)
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 95))

        # Back Button (Top Left)
        mx, my = pygame.mouse.get_pos()
        b_hover = self.back_btn.collidepoint(mx, my)
        b_col = (45, 60, 100) if b_hover else (24, 30, 52)
        pygame.draw.rect(surface, b_col, self.back_btn, border_radius=10)
        pygame.draw.rect(surface, GOLD if b_hover else (80, 105, 150), self.back_btn, 2, border_radius=10)
        b_txt = FONT.render("< MENU (ESC)", True, GOLD if b_hover else WHITE)
        surface.blit(b_txt, (self.back_btn.centerx - b_txt.get_width() // 2, self.back_btn.centery - b_txt.get_height() // 2))

        # P1 Card (Left)
        p1_elem = ELEMENT_LIST[self.p1_idx]
        self.draw_champion_card(surface, 90, 140, p1_elem, "PLAYER 1", "Press A / D to Change")

        # VS Emblem in Center
        vs_surf = TITLE_FONT.render("V S", True, (150, 175, 220))
        surface.blit(vs_surf, (WIDTH // 2 - vs_surf.get_width() // 2, 330))

        # P2 / CPU Card (Right)
        p2_elem = ELEMENT_LIST[self.p2_idx]
        p2_label = "CPU OPPONENT" if self.mode == 'VS_CPU' else "PLAYER 2"
        self.draw_champion_card(surface, WIDTH - 470, 140, p2_elem, p2_label, "Press LEFT / RIGHT to Change")

        # Start Match Button
        hover = self.start_btn.collidepoint(mx, my)
        btn_c = (55, 190, 95) if hover else (40, 145, 75)
        pygame.draw.rect(surface, btn_c, self.start_btn, border_radius=14)
        pygame.draw.rect(surface, WHITE, self.start_btn, 3, border_radius=14)
        btn_txt = HEADER_FONT.render("START BATTLE (SPACE)", True, WHITE)
        surface.blit(btn_txt, (WIDTH // 2 - btn_txt.get_width() // 2, 622))

    def draw_champion_card(self, surface, x, y, elem_key, header_title, hint_text):
        elem = ELEMENT_DATA[elem_key]
        w, h = 380, 440

        pygame.draw.rect(surface, (18, 24, 44), (x, y, w, h), border_radius=18)
        pygame.draw.rect(surface, elem['main'], (x, y, w, h), 4, border_radius=18)

        # Card Header
        lbl = FONT.render(header_title, True, (180, 205, 245))
        surface.blit(lbl, (x + w // 2 - lbl.get_width() // 2, y + 18))

        name = TITLE_FONT.render(elem['name'], True, elem['highlight'])
        surface.blit(name, (x + w // 2 - name.get_width() // 2, y + 48))

        title = SMALL_FONT.render(elem['title'], True, (210, 230, 255))
        surface.blit(title, (x + w // 2 - title.get_width() // 2, y + 105))

        # Avatar Emblem Circle
        cx, cy = x + w // 2, y + 180
        pygame.draw.circle(surface, elem['dark'], (cx, cy), 46)
        pygame.draw.circle(surface, elem['main'], (cx, cy), 44, 3)
        draw_glow(surface, cx, cy, 40, elem['main'], 0.5)
        initials = HEADER_FONT.render(elem['name'][:2], True, WHITE)
        surface.blit(initials, (cx - initials.get_width() // 2, cy - initials.get_height() // 2))

        # Stats Radar / Bar display
        stats = elem['stats']
        stat_y = y + 245
        for sname, sval in [('POWER', stats['power']), ('SPEED', stats['speed']), ('DEFENSE', stats['defense']), ('RANGE', stats['range'])]:
            s_lbl = TINY_FONT.render(sname, True, (160, 185, 220))
            surface.blit(s_lbl, (x + 35, stat_y))
            pygame.draw.rect(surface, (30, 38, 64), (x + 115, stat_y + 3, 220, 8), border_radius=3)
            pygame.draw.rect(surface, elem['highlight'], (x + 115, stat_y + 3, int(220 * sval / 100.0), 8), border_radius=3)
            stat_y += 24

        # Ultimate Move Name
        ult_lbl = TINY_FONT.render(f"OVERDRIVE: {elem['ult_name']}", True, GOLD)
        surface.blit(ult_lbl, (x + w // 2 - ult_lbl.get_width() // 2, y + 360))

        # Hint
        hint = SMALL_FONT.render(hint_text, True, (140, 165, 210))
        surface.blit(hint, (x + w // 2 - hint.get_width() // 2, y + 400))


# =====================================================
# MAIN MENU SCREEN
# =====================================================

class MainMenuScreen:
    def __init__(self):
        self.options = [
            ("ARCADE MODE", "VS_CPU_LADDER"),
            ("VS CPU BATTLE", "VS_CPU"),
            ("2-PLAYER VERSUS", "VS_P2"),
            ("TRAINING DOJO", "TRAINING"),
            ("HOW TO PLAY & CONTROLS", "HELP"),
            ("EXIT GAME", "EXIT")
        ]
        self.selected_idx = 0
        self.particles = [Particle(random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                                   random.choice([(255, 100, 30), (40, 180, 255), (60, 240, 110), (160, 60, 255)]),
                                   random.uniform(2, 5), random.randint(40, 100),
                                   vx=random.uniform(-0.5, 0.5), vy=random.uniform(-1, 0.5)) for _ in range(50)]

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_idx = (self.selected_idx - 1) % len(self.options)
                AUDIO.play('move')
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_idx = (self.selected_idx + 1) % len(self.options)
                AUDIO.play('move')
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                AUDIO.play('select')
                return self.options[self.selected_idx][1]

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, opt in enumerate(self.options):
                btn_rect = pygame.Rect(WIDTH // 2 - 200, 270 + i * 58, 400, 46)
                if btn_rect.collidepoint(mx, my):
                    AUDIO.play('select')
                    return opt[1]

        return None

    def update(self):
        for p in self.particles:
            p.update()
            if p.is_dead():
                p.x = random.uniform(0, WIDTH)
                p.y = HEIGHT
                p.lifetime = random.randint(40, 100)
                p.size = random.uniform(2, 5)

    def draw(self, surface):
        surface.fill(DARK_BG)

        for p in self.particles:
            p.draw(surface)

        # Central Elemental Glow
        draw_glow(surface, WIDTH // 2, 130, 220, (235, 75, 30), 0.3)
        draw_glow(surface, WIDTH // 2, 130, 170, (40, 180, 255), 0.3)

        # Title
        title = HUGE_FONT.render("ELEMENTAL CLASH", True, WHITE)
        overdrive = HUGE_FONT.render("O V E R D R I V E", True, GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        surface.blit(overdrive, (WIDTH // 2 - overdrive.get_width() // 2, 125))

        sub = FONT.render("THE DYNAMIC ARENA FIGHTER", True, (160, 195, 245))
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 205))

        # Menu buttons
        mx, my = pygame.mouse.get_pos()
        for i, (label, code) in enumerate(self.options):
            btn_rect = pygame.Rect(WIDTH // 2 - 200, 270 + i * 58, 400, 46)
            is_hover = btn_rect.collidepoint(mx, my) or (i == self.selected_idx)
            btn_col = (45, 60, 100) if is_hover else (22, 28, 50)
            pygame.draw.rect(surface, btn_col, btn_rect, border_radius=10)
            pygame.draw.rect(surface, GOLD if is_hover else (80, 105, 150), btn_rect, 2, border_radius=10)

            txt = HEADER_FONT.render(label, True, GOLD if is_hover else WHITE)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, btn_rect.y + 8))

        foot = SMALL_FONT.render("Use W / S or ARROWS to Select | ENTER to Confirm | M: Mute Music | N: Mute SFX", True, (130, 150, 190))
        surface.blit(foot, (WIDTH // 2 - foot.get_width() // 2, HEIGHT - 35))


# =====================================================
# HOW TO PLAY / CONTROLS HELP SCREEN
# =====================================================

def draw_help_screen(surface):
    surface.fill(DARK_BG)

    # Clickable Back Button (Top Left)
    help_back_btn = pygame.Rect(40, 25, 160, 42)
    mx, my = pygame.mouse.get_pos()
    hb_hover = help_back_btn.collidepoint(mx, my)
    pygame.draw.rect(surface, (45, 60, 100) if hb_hover else (24, 30, 52), help_back_btn, border_radius=10)
    pygame.draw.rect(surface, GOLD if hb_hover else (80, 105, 150), help_back_btn, 2, border_radius=10)
    hb_txt = FONT.render("< MENU (ESC)", True, GOLD if hb_hover else WHITE)
    surface.blit(hb_txt, (help_back_btn.centerx - hb_txt.get_width() // 2, help_back_btn.centery - hb_txt.get_height() // 2))

    title = HUGE_FONT.render("HOW TO PLAY & CONTROLS", True, GOLD)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 35))

    p1_card = pygame.Rect(80, 130, 480, 450)
    p2_card = pygame.Rect(640, 130, 480, 450)

    # P1 Controls
    pygame.draw.rect(surface, (20, 26, 48), p1_card, border_radius=14)
    pygame.draw.rect(surface, (80, 140, 245), p1_card, 3, border_radius=14)
    p1_lbl = TITLE_FONT.render("PLAYER 1 CONTROLS", True, (120, 190, 255))
    surface.blit(p1_lbl, (p1_card.x + 30, p1_card.y + 25))

    p1_moves = [
        ("W / S / A / D", "Move, Jump & Fast-Fall"),
        ("LEFT SHIFT / SPACE", "Flash Dash (Invulnerable)"),
        ("TAP F", "Primary Projectile"),
        ("HOLD & RELEASE F", "Super Charged Beam"),
        ("G KEY", "Rapid Skill Barrage"),
        ("E KEY", "Shield (Tap on impact for PERFECT PARRY!)"),
        ("Q KEY", "OVERDRIVE ULTIMATE (When 100% Burst)"),
    ]
    for idx, (k, desc) in enumerate(p1_moves):
        kt = FONT.render(k, True, GOLD)
        dt = SMALL_FONT.render(desc, True, WHITE)
        surface.blit(kt, (p1_card.x + 30, p1_card.y + 90 + idx * 46))
        surface.blit(dt, (p1_card.x + 30, p1_card.y + 114 + idx * 46))

    # P2 Controls
    pygame.draw.rect(surface, (20, 26, 48), p2_card, border_radius=14)
    pygame.draw.rect(surface, (245, 90, 70), p2_card, 3, border_radius=14)
    p2_lbl = TITLE_FONT.render("PLAYER 2 CONTROLS", True, (255, 140, 120))
    surface.blit(p2_lbl, (p2_card.x + 30, p2_card.y + 25))

    p2_moves = [
        ("ARROW KEYS", "Move, Jump & Fast-Fall"),
        ("RIGHT SHIFT / /", "Flash Dash (Invulnerable)"),
        ("TAP ENTER", "Primary Projectile"),
        ("HOLD & RELEASE ENTER", "Super Charged Beam"),
        ("RSHIFT / \\", "Rapid Skill Barrage"),
        ("RIGHT CTRL", "Shield (Tap on impact for PERFECT PARRY!)"),
        ("BACKSPACE / RALT", "OVERDRIVE ULTIMATE (When 100% Burst)"),
    ]
    for idx, (k, desc) in enumerate(p2_moves):
        kt = FONT.render(k, True, GOLD)
        dt = SMALL_FONT.render(desc, True, WHITE)
        surface.blit(kt, (p2_card.x + 30, p2_card.y + 90 + idx * 46))
        surface.blit(dt, (p2_card.x + 30, p2_card.y + 114 + idx * 46))

    back_txt = HEADER_FONT.render("Press ESC or SPACE to Return to Main Menu", True, (210, 230, 255))
    surface.blit(back_txt, (WIDTH // 2 - back_txt.get_width() // 2, 620))


# =====================================================
# GAME STATE MANAGER & MAIN LOOP
# =====================================================

def run_game(max_frames=None):
    global game_state, player1, player2, current_stage, projectiles, beams
    global particles, shockwaves, ghost_trails, ground_decals, floating_texts
    global clash_manager, active_ultimate, game_over, winner_text, match_timer
    global arcade_current_step, shake_timer, hitstop_timer

    game_state = "MENU"
    menu_screen = MainMenuScreen()
    selection_screen = SelectionScreen()

    player1 = None
    player2 = None
    current_stage = None
    projectiles = []
    beams = []
    particles = []
    shockwaves = []
    ghost_trails = []
    ground_decals = []
    floating_texts = []
    clash_manager = BeamClashManager()
    active_ultimate = None

    game_over = False
    winner_text = ""
    match_timer = 99.0
    arcade_stage_ladder = ['fire', 'water', 'earth', 'lightning']
    arcade_current_step = 0

    running = True
    frame_count = 0

    while running:
        frame_count += 1
        if max_frames and frame_count > max_frames:
            break

            # -------------------------------------------------
            # GLOBAL EVENT HANDLING
            # -------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    AUDIO.toggle_music()
                elif event.key == pygame.K_n:
                    AUDIO.toggle_sfx()

            if game_state == "MENU":
                action = menu_screen.handle_input(event)
                if action == "VS_CPU":
                    selection_screen.mode = "VS_CPU"
                    game_state = "SELECTION"
                elif action == "VS_P2":
                    selection_screen.mode = "VS_P2"
                    game_state = "SELECTION"
                elif action == "ARCADE_MODE" or action == "VS_CPU_LADDER":
                    selection_screen.mode = "ARCADE"
                    arcade_current_step = 0
                    game_state = "SELECTION"
                elif action == "TRAINING":
                    selection_screen.mode = "TRAINING"
                    game_state = "SELECTION"
                elif action == "HELP":
                    game_state = "HELP"
                elif action == "EXIT":
                    running = False

            elif game_state == "HELP":
                help_back_btn = pygame.Rect(40, 25, 160, 42)
                if event.type == pygame.KEYDOWN and (event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN, pygame.K_b)):
                    AUDIO.play('move')
                    game_state = "MENU"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if help_back_btn.collidepoint(event.pos):
                        AUDIO.play('move')
                        game_state = "MENU"

            elif game_state == "SELECTION":
                sel_action = selection_screen.handle_input(event)
                if sel_action == "BACK":
                    game_state = "MENU"
                elif sel_action == "START":
                    # Initialize Match
                    p1_elem = ELEMENT_LIST[selection_screen.p1_idx]
                    p2_elem = ELEMENT_LIST[selection_screen.p2_idx]
                    stage_key = selection_screen.stages[selection_screen.stage_idx]

                    is_cpu_match = (selection_screen.mode in ['VS_CPU', 'ARCADE', 'TRAINING'])
                    diff = selection_screen.ai_difficulty if selection_screen.mode != 'ARCADE' else ['apprentice', 'normal', 'grandmaster', 'grandmaster'][arcade_current_step]

                    player1 = Champion(260, GROUND_Y - 45, p1_elem, is_player_one=True, is_cpu=False)
                    player2 = Champion(940, GROUND_Y - 45, p2_elem, is_player_one=False, is_cpu=is_cpu_match, cpu_difficulty=diff)

                    current_stage = ArenaStage(stage_key)
                    projectiles.clear()
                    beams.clear()
                    particles.clear()
                    shockwaves.clear()
                    ghost_trails.clear()
                    ground_decals.clear()
                    floating_texts.clear()
                    active_ultimate = None
                    clash_manager = BeamClashManager()

                    game_over = False
                    winner_text = ""
                    match_timer = 99.0
                    game_state = "BATTLE"

            elif game_state == "BATTLE":
                hud_menu_btn = pygame.Rect(WIDTH // 2 - 48, 64, 96, 22)
                rematch_btn = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 + 95, 230, 48)
                menu_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 95, 230, 48)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hud_menu_btn.collidepoint(event.pos):
                        AUDIO.play('move')
                        game_state = "MENU"
                    elif game_over:
                        if menu_btn.collidepoint(event.pos):
                            AUDIO.play('move')
                            game_state = "MENU"
                        elif rematch_btn.collidepoint(event.pos):
                            if selection_screen.mode == 'ARCADE' and player1.hp > 0 and arcade_current_step < len(arcade_stage_ladder) - 1:
                                arcade_current_step += 1
                                next_elem = arcade_stage_ladder[arcade_current_step]
                                player2 = Champion(940, GROUND_Y - 45, next_elem, is_player_one=False, is_cpu=True, cpu_difficulty='grandmaster')
                                current_stage = ArenaStage(next_elem)
                                player1.hp = min(player1.max_hp, player1.hp + 60)
                                game_over = False
                                match_timer = 99.0
                            else:
                                game_state = "SELECTION"
                                game_over = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        AUDIO.play('move')
                        game_state = "MENU"

                    elif game_over:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                            if selection_screen.mode == 'ARCADE' and player1.hp > 0 and arcade_current_step < len(arcade_stage_ladder) - 1:
                                # Advance to next arcade stage
                                arcade_current_step += 1
                                next_elem = arcade_stage_ladder[arcade_current_step]
                                player2 = Champion(940, GROUND_Y - 45, next_elem, is_player_one=False, is_cpu=True, cpu_difficulty='grandmaster')
                                current_stage = ArenaStage(next_elem)
                                player1.hp = min(player1.max_hp, player1.hp + 60)
                                game_over = False
                                match_timer = 99.0
                            else:
                                game_state = "SELECTION"
                                game_over = False

                    elif not game_over:
                        # Player 1 Controls
                        if event.key == pygame.K_w:
                            player1.jump()
                        elif event.key == pygame.K_LSHIFT or event.key == pygame.K_SPACE or event.key == pygame.K_c:
                            player1.dash(ghost_trails)
                        elif event.key == pygame.K_e:
                            player1.trigger_shield()
                        elif event.key == pygame.K_g:
                            player1.trigger_barrage()
                        elif event.key == pygame.K_q:
                            if player1.burst >= 100.0 and active_ultimate is None:
                                active_ultimate = player1.trigger_ultimate(player2)
                        elif event.key == pygame.K_f:
                            if clash_manager.active:
                                clash_manager.push(0.08)  # Beam mash push!
                            else:
                                player1.charging = True
                                player1.charge_time = 0

                        # Player 2 Controls (when not CPU)
                        if not player2.is_cpu:
                            if event.key == pygame.K_UP:
                                player2.jump()
                            elif event.key == pygame.K_RSHIFT or event.key == pygame.K_SLASH:
                                player2.dash(ghost_trails)
                            elif event.key == pygame.K_RCTRL:
                                player2.trigger_shield()
                            elif event.key == pygame.K_BACKSLASH or event.key == pygame.K_PERIOD:
                                player2.trigger_barrage()
                            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_RALT:
                                if player2.burst >= 100.0 and active_ultimate is None:
                                    active_ultimate = player2.trigger_ultimate(player1)
                            elif event.key == pygame.K_RETURN:
                                if clash_manager.active:
                                    clash_manager.push(-0.08)  # Beam mash push!
                                else:
                                    player2.charging = True
                                    player2.charge_time = 0

                elif event.type == pygame.KEYUP and not game_over:
                    if event.key == pygame.K_f and player1.charging:
                        attack = player1.release_attack()
                        if isinstance(attack, Beam):
                            beams.append(attack)
                        elif isinstance(attack, Projectile):
                            projectiles.append(attack)

                    if not player2.is_cpu and event.key == pygame.K_RETURN and player2.charging:
                        attack = player2.release_attack()
                        if isinstance(attack, Beam):
                            beams.append(attack)
                        elif isinstance(attack, Projectile):
                            projectiles.append(attack)

        # -------------------------------------------------
        # MENU & UI UPDATES
        # -------------------------------------------------
        if game_state == "MENU":
            menu_screen.update()
            menu_screen.draw(screen)

        elif game_state == "HELP":
            draw_help_screen(screen)

        elif game_state == "SELECTION":
            selection_screen.draw(screen)

        # -------------------------------------------------
        # BATTLE SIMULATION
        # -------------------------------------------------
        elif game_state == "BATTLE":
            if not game_over:
                if hitstop_timer > 0:
                    hitstop_timer -= 1
                else:
                    match_timer = max(0.0, match_timer - 1.0 / FPS)

                    # Continuous Key Movement
                    keys = pygame.key.get_pressed()
                    # P1
                    dx1 = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
                    if dx1 != 0:
                        player1.vx += dx1 * 1.6
                        player1.vx = max(-player1.speed, min(player1.speed, player1.vx))

                    # P2
                    if not player2.is_cpu:
                        dx2 = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
                        if dx2 != 0:
                            player2.vx += dx2 * 1.6
                            player2.vx = max(-player2.speed, min(player2.speed, player2.vx))
                    else:
                        player2.update_cpu_ai(player1, projectiles, beams, ghost_trails)

                    current_stage.update()

                    # Update entities
                    player1.update_physics(ghost_trails, particles)
                    player2.update_physics(ghost_trails, particles)
                    player1.update_attack_state(projectiles, particles)
                    player2.update_attack_state(projectiles, particles)

                    # CPU Ultimate Trigger
                    if player2.is_cpu and player2.ai_action == 'ultimate' and active_ultimate is None:
                        active_ultimate = player2.trigger_ultimate(player1)
                        player2.ai_action = 'idle'

                    # Active Ultimate
                    if active_ultimate:
                        active_ultimate.update(particles, shockwaves, ground_decals)
                        if active_ultimate.is_finished():
                            active_ultimate = None

                    # Clashing & Beam struggle
                    if clash_manager.active:
                        clash_manager.update(particles, shockwaves, floating_texts)
                        # CPU mash during clash
                        if player2.is_cpu and random.random() < 0.45:
                            clash_manager.push(-0.04)

                    for proj in projectiles[:]:
                        proj.update(particles)
                        if proj.is_finished():
                            projectiles.remove(proj)

                    for beam in beams[:]:
                        beam.update(particles)
                        if beam.is_finished():
                            beams.remove(beam)

                    resolve_combat_interactions(projectiles, beams, [player1, player2], particles, shockwaves, floating_texts, clash_manager)

                    for p in particles[:]:
                        p.update()
                        if p.is_dead():
                            particles.remove(p)

                    for s in shockwaves[:]:
                        s.update()
                        if s.is_dead():
                            shockwaves.remove(s)

                    for g in ghost_trails[:]:
                        g.update()
                        if g.is_dead():
                            ghost_trails.remove(g)

                    for d in ground_decals[:]:
                        d.update()
                        if d.is_dead():
                            ground_decals.remove(d)

                    for f in floating_texts[:]:
                        f.update()
                        if f.is_dead():
                            floating_texts.remove(f)

                    # Check KO / Game Over
                    if player1.hp <= 0 or player2.hp <= 0 or match_timer <= 0:
                        game_over = True
                        trigger_shake(4, 6)
                        trigger_hitstop(10)
                        AUDIO.play('ko')
                        if player1.hp > player2.hp:
                            winner_text = f"PLAYER 1 ({ELEMENT_DATA[player1.element_type]['name']}) VICTORY!"
                        elif player2.hp > player1.hp:
                            winner_tag = "CPU" if player2.is_cpu else "PLAYER 2"
                            winner_text = f"{winner_tag} ({ELEMENT_DATA[player2.element_type]['name']}) VICTORY!"
                        else:
                            winner_text = "TIME UP - DRAW MATCH!"

            if shake_timer > 0:
                shake_timer -= 1

            # -------------------------------------------------
            # RENDER BATTLE SCENE
            # -------------------------------------------------
            current_stage.draw(game_surface)

            for d in ground_decals:
                d.draw(game_surface)

            for g in ghost_trails:
                g.draw(game_surface)

            for p in particles:
                p.draw(game_surface)

            for proj in projectiles:
                proj.draw(game_surface)

            for beam in beams:
                beam.draw(game_surface)

            for s in shockwaves:
                s.draw(game_surface)

            player1.draw(game_surface, player2)
            player2.draw(game_surface, player1)

            clash_manager.draw(game_surface)

            if active_ultimate:
                active_ultimate.draw(game_surface)

            for f in floating_texts:
                f.draw(game_surface)

            # Draw Sleek Battle HUD
            draw_battle_hud(game_surface, player1, player2, match_timer, current_stage.name)

            # Game Over Victory Screen Overlay
            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 12, 24, 210))
                game_surface.blit(overlay, (0, 0))

                win_title = HUGE_FONT.render("K. O.", True, CRIT_RED)
                win_sub = TITLE_FONT.render(winner_text, True, GOLD)

                is_arcade_advance = (selection_screen.mode == 'ARCADE' and player1.hp > 0 and arcade_current_step < len(arcade_stage_ladder) - 1)

                # Match statistics breakdown
                stats_p1 = SMALL_FONT.render(f"P1: {player1.total_damage_dealt} Dmg Dealt | {player1.parries_landed} Parries", True, (180, 215, 255))
                stats_p2 = SMALL_FONT.render(f"P2: {player2.total_damage_dealt} Dmg Dealt | {player2.parries_landed} Parries", True, (255, 180, 180))

                game_surface.blit(win_title, (WIDTH // 2 - win_title.get_width() // 2, HEIGHT // 2 - 130))
                game_surface.blit(win_sub, (WIDTH // 2 - win_sub.get_width() // 2, HEIGHT // 2 - 50))
                game_surface.blit(stats_p1, (WIDTH // 2 - stats_p1.get_width() // 2, HEIGHT // 2 + 15))
                game_surface.blit(stats_p2, (WIDTH // 2 - stats_p2.get_width() // 2, HEIGHT // 2 + 40))

                # Interactive Clickable Buttons on Game Over
                rematch_btn = pygame.Rect(WIDTH // 2 - 245, HEIGHT // 2 + 85, 230, 48)
                menu_btn = pygame.Rect(WIDTH // 2 + 15, HEIGHT // 2 + 85, 230, 48)

                mx, my = pygame.mouse.get_pos()
                r_hover = rematch_btn.collidepoint(mx, my)
                m_hover = menu_btn.collidepoint(mx, my)

                r_col = (45, 175, 85) if r_hover else (30, 130, 65)
                m_col = (180, 55, 60) if m_hover else (125, 38, 42)

                pygame.draw.rect(game_surface, r_col, rematch_btn, border_radius=12)
                pygame.draw.rect(game_surface, WHITE if r_hover else (180, 240, 190), rematch_btn, 2, border_radius=12)
                r_btn_txt = HEADER_FONT.render("NEXT STAGE" if is_arcade_advance else "REMATCH (SPACE)", True, WHITE)
                game_surface.blit(r_btn_txt, (rematch_btn.centerx - r_btn_txt.get_width() // 2, rematch_btn.centery - r_btn_txt.get_height() // 2))

                pygame.draw.rect(game_surface, m_col, menu_btn, border_radius=12)
                pygame.draw.rect(game_surface, WHITE if m_hover else (240, 180, 180), menu_btn, 2, border_radius=12)
                m_btn_txt = HEADER_FONT.render("< MAIN MENU (ESC)", True, WHITE)
                game_surface.blit(m_btn_txt, (menu_btn.centerx - m_btn_txt.get_width() // 2, menu_btn.centery - m_btn_txt.get_height() // 2))

            # Blit with Screen Shake offset (Steady on Game Over)
            sx, sy = get_shake_offset()
            if game_over:
                sx, sy = 0, 0  # Completely eliminate shake after match is complete!
            screen.fill(BLACK)
            screen.blit(game_surface, (sx, sy))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_game()
