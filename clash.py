import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elemental Clash: Fire vs Water")
clock = pygame.time.Clock()

# Colors
BLACK = (10, 10, 15)
WHITE = (255, 255, 255)
FIRE_COLORS = [(255, 50, 0), (255, 120, 0), (255, 200, 0)]
WATER_COLORS = [(0, 100, 255), (0, 180, 255), (100, 220, 255)]

class Particle:
    def __init__(self, x, y, color, size, life, speed_x, speed_y):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.original_life = life
        self.life = life
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        # Shrink over time
        self.size = max(0, self.size - 0.2)

    def draw(self, surface):
        if self.size > 0:
            alpha = int((self.life / self.original_life) * 255)
            # Create a temporary surface for alpha blending to make it look fluid
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class Projectile:
    def __init__(self, x, y, direction, is_fire, is_charged):
        self.x = x
        self.y = y
        self.direction = direction
        self.is_fire = is_fire
        self.is_charged = is_charged
        self.active = True
        
        if self.is_charged:
            self.speed = 8 * direction
            self.width = 40
            self.height = 200 # Giant fluid curtain AoE
            self.damage = 30
        else:
            self.speed = 15 * direction
            self.width = 20
            self.height = 20
            self.damage = 10

        self.rect = pygame.Rect(self.x, self.y - self.height//2, self.width, self.height)

    def update(self, particles):
        self.x += self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y - self.height // 2)

        if self.x < -100 or self.x > WIDTH + 100:
            self.active = False

        # Fluid particle generation
        colors = FIRE_COLORS if self.is_fire else WATER_COLORS
        if self.is_charged:
            # Generate a "curtain" of fluid particles up and down the height of the AoE
            for _ in range(8):
                offset_y = random.randint(-self.height//2, self.height//2)
                particles.append(Particle(
                    self.x + random.randint(-10, 10), 
                    self.y + offset_y, 
                    random.choice(colors), 
                    random.randint(10, 20), 
                    random.randint(15, 30),
                    random.uniform(-1, 1) * self.direction, 
                    random.uniform(-2, 2)
                ))
        else:
            # Generate normal trail
            for _ in range(3):
                particles.append(Particle(
                    self.x, self.y + random.randint(-5, 5), 
                    random.choice(colors), 
                    random.randint(5, 12), 
                    random.randint(10, 20),
                    random.uniform(-2, 0) * self.direction, 
                    random.uniform(-1, 1)
                ))

class Player:
    def __init__(self, x, y, is_fire):
        self.x = x
        self.y = y
        self.is_fire = is_fire
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.speed = 6
        self.hp = 100
        
        self.charging = False
        self.charge_time = 0
        self.charge_threshold = 45 # Frames needed for a charged attack (~0.75 seconds)

    def move(self, up_key, down_key, keys):
        if keys[up_key] and self.rect.top > 50:
            self.y -= self.speed
        if keys[down_key] and self.rect.bottom < HEIGHT - 50:
            self.y += self.speed
        self.rect.centery = self.y

    def update_charge(self, particles):
        if self.charging:
            self.charge_time += 1
            # Visual charging effect
            colors = FIRE_COLORS if self.is_fire else WATER_COLORS
            radius = min(40, self.charge_time)
            
            # Spawn energy gathering particles
            angle = random.uniform(0, math.pi * 2)
            dist = random.randint(20, max(21, int(radius)))
            px = self.x + math.cos(angle) * dist
            py = self.y + math.sin(angle) * dist
            
            particles.append(Particle(
                px, py, random.choice(colors), 
                random.randint(3, 6), 10,
                (self.x - px) * 0.1, (self.y - py) * 0.1
            ))

    def release_attack(self):
        is_charged = self.charge_time >= self.charge_threshold
        direction = 1 if self.is_fire else -1
        proj = Projectile(self.x + (30 * direction), self.y, direction, self.is_fire, is_charged)
        self.charging = False
        self.charge_time = 0
        return proj

    def draw(self, surface):
        color = FIRE_COLORS[0] if self.is_fire else WATER_COLORS[0]
        # Draw player block
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw charge aura if fully charged
        if self.charging and self.charge_time >= self.charge_threshold:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 30, 3)

def draw_health_bars(surface, p1, p2):
    # P1 Health (Left)
    pygame.draw.rect(surface, (100, 100, 100), (50, 20, 300, 20))
    if p1.hp > 0:
        pygame.draw.rect(surface, FIRE_COLORS[0], (50, 20, p1.hp * 3, 20))
    
    # P2 Health (Right)
    pygame.draw.rect(surface, (100, 100, 100), (WIDTH - 350, 20, 300, 20))
    if p2.hp > 0:
        pygame.draw.rect(surface, WATER_COLORS[0], (WIDTH - 350 + (100 - p2.hp)*3, 20, p2.hp * 3, 20))

def main():
    player1 = Player(100, HEIGHT // 2, is_fire=True)
    player2 = Player(WIDTH - 100, HEIGHT // 2, is_fire=False)
    
    projectiles = []
    particles = []
    
    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Key Presses (Start Charging)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player1.charging = True
                if event.key == pygame.K_RETURN:
                    player2.charging = True
                    
            # Key Releases (Shoot)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and player1.charging:
                    projectiles.append(player1.release_attack())
                if event.key == pygame.K_RETURN and player2.charging:
                    projectiles.append(player2.release_attack())

        keys = pygame.key.get_pressed()
        
        # Movement
        player1.move(pygame.K_w, pygame.K_s, keys)
        player2.move(pygame.K_UP, pygame.K_DOWN, keys)

        # Update charge logic
        player1.update_charge(particles)
        player2.update_charge(particles)

        # Update Projectiles & Check Collisions
        for proj in projectiles[:]:
            proj.update(particles)
            
            # Collision with Player 2
            if proj.is_fire and proj.rect.colliderect(player2.rect):
                player2.hp -= proj.damage
                proj.active = False
            
            # Collision with Player 1
            if not proj.is_fire and proj.rect.colliderect(player1.rect):
                player1.hp -= proj.damage
                proj.active = False
                
            if not proj.active:
                # Explosion particles on hit
                colors = FIRE_COLORS if proj.is_fire else WATER_COLORS
                for _ in range(20 if proj.is_charged else 10):
                    particles.append(Particle(
                        proj.x, proj.y + random.randint(-proj.height//2, proj.height//2),
                        random.choice(colors), random.randint(5, 15), random.randint(15, 30),
                        random.uniform(-3, 3), random.uniform(-3, 3)
                    ))
                projectiles.remove(proj)

        # Update Particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)

        # Win condition check
        if player1.hp <= 0 or player2.hp <= 0:
            print("Game Over!")
            running = False

        # Drawing
        screen.fill(BLACK)
        
        # Draw particles behind players
        for particle in particles:
            particle.draw(screen)
            
        player1.draw(screen)
        player2.draw(screen)
        draw_health_bars(screen, player1, player2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
