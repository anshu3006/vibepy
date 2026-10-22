# ⚡ ELEMENTAL CLASH: OVERDRIVE ⚡
### A Full-Fledged 2D Arena Fighter with Dynamic Graphics & Combat Physics

---

## 🎮 Overview

**Elemental Clash: Overdrive** is a high-octane, stylish 2D elemental arena fighter featuring procedural character graphics, cloth physics, dynamic lighting with radial bloom, multi-layer animated arenas, procedural audio synthesis, aerial jump & dash physics, an interactive beam clash struggle, and devastating Overdrive Ultimates.

---

## 🌟 Key Features

### 1. 🎨 Dynamic Visuals & Graphics Engine
- **Procedural Animated Champions**: Multi-node flowing cloth physics cape, articulated running legs, dynamic jump poses, glowing elemental chest cores, custom head crests/horns, and 3D orbiting elemental catalysts.
- **Dynamic Lighting & Bloom**: Multi-level additive glow rendering on projectiles, beams, magic circles, and impacts.
- **Multi-Layer Dynamic Arenas**:
  - **Caldera of Ignis (Fire)**: Molten lava river with sine-wave ripples, basalt crags, and rising floating embers.
  - **Abyssal Sanctuary (Water)**: Underwater light shafts, coral spires, and luminescent rising bubbles.
  - **Tempest Peaks (Lightning)**: Mountain fortresses under real-time procedural lightning storm flashes and rain streaks.
  - **Astral Void Nexus (Cosmic)**: Multi-ring rotating celestial clockwork and interstellar nebula glows.
- **Visual Juice**:
  - Screen shake with trauma decay.
  - Hitstop impact freeze-frames on heavy collisions.
  - Expanding shockwave rings & ground scorch marks.
  - Dynamic bouncy floating damage text with critical hit notifications.
  - Ghost trails (fading colored after-images) during high-speed dashes.

### 2. ⚔️ Deep Combat & Dynamics
- **Full 2D Physics**: Velocity-based movement, variable jumping (`W` / `UP`), fast-fall (`S` / `DOWN`), and aerodynamic flash dashes with invulnerability frames (`Shift` / `Space`).
- **5 Elemental Champions**:
  - 🔥 **Ignis (Fire)**: *Solar Comet*, *Inferno Volley*, *Solar Flare Ray*, and **SUPERNOVA APOCALYPSE**.
  - 💧 **Aquaris (Water)**: *Hydro Lance*, *Torrent Surge*, *Tidal Maelstrom*, and **LEVIATHAN DELUGE**.
  - 🌿 **Terran (Earth)**: *Geo Boulder*, *Fissure Spikes*, *Tectonic Cannon*, and **CATACLYSMIC QUAKE**.
  - ⚡ **Volt (Lightning)**: *Plasma Bolt*, *Chain Discharge*, *Thunder God Railgun*, and **JUDGMENT OF RAIJIN**.
  - 🌪️ **Zephyr (Wind)**: *Gale Crescent*, *Whirlwind Burst*, *Vortex Hurricane*, and **TEMPEST CATACLYSM**.
- **Interactive Beam Clash Struggle**:
  - When opposing beams collide, they lock into an arcade struggle!
  - Both players (or CPU) rapidly mash their attack button to push the collision point toward the opponent.
  - Pushing past the threshold triggers a massive **CLASH BREAKTHROUGH** explosion!
- **Perfect Parry System**:
  - Activating the shield within 7 frames (0.11s) of an incoming projectile performs a **PERFECT PARRY**:
    - Completely negates all damage with a resonant golden chime.
    - Reverses the projectile back toward the attacker with **1.5x speed and damage**!
    - Instantly restores 35 stamina and awards 25% Overdrive Burst!
- **Overdrive Super Moves (Ultimates)**:
  - Dealing and taking damage charges the Burst Gauge up to 100%.
  - Pressing `Q` (P1) or `Backspace` (P2) pauses the screen with an anime-style cut-in banner, unleashing an apocalyptic screen-wide super attack.

### 3. 🕹️ Game Modes
- **ARCADE MODE**: Gauntlet against 4 consecutive elemental bosses with escalating AI difficulty, health carries, and victory ranking.
- **VS CPU BATTLE**: Customizable quick matches against 3 distinct AI personalities (*Apprentice*, *Normal*, and *Grandmaster*).
- **2-PLAYER VERSUS**: Local 2-player arcade couch duel on one keyboard.
- **TRAINING DOJO**: Free practice dojo with infinite stamina and practice dummies.
- **HOW TO PLAY & CONTROLS**: Full in-game interactive visual move guide.

### 4. 🔊 Procedural Audio Synthesizer
- Built-in 16-bit 22.05kHz procedural audio engine (no external audio files required).
- 12 unique SFX (Shooting, Beam roar, Shield hum, Perfect Parry chime, Dash whoosh, Clash buzz, Explosions, K.O. bass drop).
- Driving electronic synthwave battle soundtrack looping seamlessly in the background.
- Music toggle (`M`) and SFX toggle (`N`).

---

## 🕹️ Controls

### Player 1 (Left Side):
| Action | Key |
| :--- | :--- |
| **Move Left / Right** | `A` / `D` |
| **Jump** | `W` |
| **Fast Fall** | `S` |
| **Flash Dash (i-frames)** | `Left Shift` / `Space` / `C` |
| **Primary Projectile** | `Tap F` |
| **Super Charged Beam** | `Hold & Release F` |
| **Skill Barrage** | `G` |
| **Shield / Perfect Parry** | `E` |
| **OVERDRIVE ULTIMATE** | `Q` *(when Burst is 100%)* |
| **Beam Clash Mash** | `Mash F` |

### Player 2 (Right Side / Versus Mode):
| Action | Key |
| :--- | :--- |
| **Move Left / Right** | `Left Arrow` / `Right Arrow` |
| **Jump** | `Up Arrow` |
| **Fast Fall** | `Down Arrow` |
| **Flash Dash (i-frames)** | `Right Shift` / `/` |
| **Primary Projectile** | `Tap Enter` |
| **Super Charged Beam** | `Hold & Release Enter` |
| **Skill Barrage** | `\` or `.` |
| **Shield / Perfect Parry** | `Right Ctrl` |
| **OVERDRIVE ULTIMATE** | `Backspace` or `Right Alt` *(when Burst is 100%)* |
| **Beam Clash Mash** | `Mash Enter` |

### Global Keys & Navigation:
- `< MENU (ESC)`: Clickable Back Button on Selection, Help, Battle HUD, and Game Over screens
- `M`: Toggle Music On/Off
- `N`: Toggle Sound Effects On/Off
- `ESC` / `B`: Return to Main Menu
- `SPACE` / `R`: Quick Rematch / Advance Stage

---

## 🚀 How to Run

Simply open terminal in this folder and run:

```bash
python clash.py
```
