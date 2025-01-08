import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 10
PLAYER_SPEED = 7

BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_SPEED = 10

ENEMY_WIDTH = 40
ENEMY_HEIGHT = 20
ENEMY_SPEED = 2
NUM_ENEMIES = 8

# Initialize screen and mixer
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('EmilyBlaster')
pygame.mixer.init()

# Clock for FPS control
clock = pygame.time.Clock()

# Load background image
background_image = pygame.image.load('bg_1.png')

# Load sound effects
splat = pygame.mixer.Sound('splat2.wav')

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('quill.png').convert_alpha()
        # self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        # self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        # self.rect = self.image.get_rect()
        # self.rect.centerx = SCREEN_WIDTH // 2
        # self.rect.bottom = SCREEN_HEIGHT - 10
        self.rect.top = SCREEN_HEIGHT - self.rect.height
        self.rect.centerx = SCREEN_WIDTH // 2
        self.speed_x = 0

    def update(self):
        keys = pygame.key.get_pressed()
        self.speed_x = 0
        if keys[pygame.K_LEFT]:
            self.speed_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.speed_x = PLAYER_SPEED
        self.rect.x += self.speed_x
        # Prevent player from going off screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -BULLET_SPEED

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = ENEMY_SPEED if random.choice([True, False]) else -ENEMY_SPEED

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speed_x *= -1

# Initialize sprites
player = Player()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Create enemies
for i in range(NUM_ENEMIES):
    x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
    y = random.randint(20, 200)
    enemy = Enemy(x, y)
    enemies.add(enemy)

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemies)

# Game loop
running = True
score = 0
font = pygame.font.SysFont(None, 36)

while running:
    clock.tick(60)

    # Check for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Shoot bullet
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

    # Update sprites
    all_sprites.update()

    # Check for collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    if len(hits) > 0:
        splat.play()
    for hit in hits:
        score += 1
        # Spawn a new enemy at a random position
        x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
        y = random.randint(20, 200)
        enemy = Enemy(x, y)
        enemies.add(enemy)
        all_sprites.add(enemy)

    # Draw everything
    bg_x = (SCREEN_WIDTH - background_image.get_width()) // 2
    bg_y = (SCREEN_HEIGHT - background_image.get_height()) // 2
    screen.blit(background_image, (bg_x, bg_y))
    all_sprites.draw(screen)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Refresh display
    pygame.display.flip()

pygame.quit()
