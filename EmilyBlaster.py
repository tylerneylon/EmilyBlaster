''' EmilyBlaster.py

    This is a pixel art retro game based on the description of Sadie Green's
    first college-made game in the book Tomorrow, and Tomorrow, and Tomorrow by
    Gabrielle Zevin.
'''


# ______________________________________________________________________
# Imports

import pygame
import random

from nineslice import NineSlice


# ______________________________________________________________________
# Globals and constants

# Screen dimensions
SCREEN_WIDTH  = 1024
SCREEN_HEIGHT =  768

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (128, 128, 128)
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

# Some poetry
# I plan to later put this into a separate file.
poem1 = '''Because I could not stop for Death -
He kindly stopped for me -
The Carriage held but just Ourselves -
And Immortality.'''


# ______________________________________________________________________
# Initialization

# Initialize pygame
pygame.init()

# Load font
font_path = 'dogicapixel.ttf'
main_font = pygame.font.Font(font_path, 20)
screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.DOUBLEBUF,
        vsync=True
)
pygame.display.set_caption('EmilyBlaster')
pygame.mixer.init()

# Clock for FPS control
clock = pygame.time.Clock()

# Load background image
background_image = pygame.image.load('bg_1.png')

# Load sound effects
splat = pygame.mixer.Sound('splat2.wav')


# ______________________________________________________________________
# Classes

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

        # Allow player to go slightly off screen.
        self.min_x = -70
        self.max_x = SCREEN_WIDTH + 10

    def update(self):
        keys = pygame.key.get_pressed()
        self.speed_x = 0
        if keys[pygame.K_LEFT]:
            self.speed_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.speed_x = PLAYER_SPEED
        self.rect.x += self.speed_x
        # Prevent player from going off screen
        if self.rect.left < self.min_x:
            self.rect.left = self.min_x
        if self.rect.right > self.max_x:
            self.rect.right = self.max_x

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
        bg_nineslice = NineSlice('word_box_6.png', (52, 27), (55, 29))
        text_surface = main_font.render("hi there", True, (80, 60, 30))
        text_w, text_h = text_surface.get_width(), text_surface.get_height()
        pad_w, pad_h = 40, 25
        w = max(text_w + pad_w, bg_nineslice.minwidth)
        h = max(text_h + pad_h, bg_nineslice.minheight)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        bg_nineslice.draw(self.image, 0, 0, w, h)
        self.image.blit(text_surface, ((w - text_w) // 2, (h - text_h) // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = random.choice([-1, 1]) * ENEMY_SPEED

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speed_x *= -1

WHITE_W_ALPHA = (255, 255, 255, 32)

class Poem(pygame.sprite.Sprite):
    def __init__(self, poem):
        super().__init__()

        self.interline_skip = 10
        p = self.padding = 10
        w, h = self.get_text_size(poem)
        w, h = w + 2 * p, h + 2 * p

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # self.image.fill(WHITE)
        pygame.draw.rect(self.image, WHITE, (0, 0, w, h), border_radius=p)

        self.render_text(poem, BLACK, 255, (p + 2, p    ))
        self.render_text(poem, WHITE, 255, (p    , p + 2))
        self.render_text(poem, GRAY , 255, (p + 1, p + 1))
        self.image.set_alpha(96)

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT // 2

    def render_text(self, text, color, alpha, position):
        lines = text.split('\n')
        y_offset = 0
        for line in lines:
            pos = (position[0], position[1] + y_offset)
            text_surface = main_font.render(line, False, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(topleft=pos)
            self.image.blit(text_surface, text_rect)
            y_offset += text_surface.get_height() + self.interline_skip

    def get_text_size(self, text):
        lines = text.split('\n')
        w, h = 2, 2  # Start height at 2 to account for embossing offsets.
        for i, line in enumerate(lines):
            text_surface = main_font.render(line, False, WHITE)
            w = max(w, text_surface.get_width() + 2)
            h += text_surface.get_height()
            if i > 0:
                h += self.interline_skip
        return w, h


# ______________________________________________________________________
# Main game code

# Initialize sprites
player = Player()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
poem = Poem(poem1)

# Create enemies
for i in range(NUM_ENEMIES):
    x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
    y = random.randint(20, 200)
    enemy = Enemy(x, y)
    enemies.add(enemy)

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(enemies)
all_sprites.add(poem)

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
                bullet = Bullet(player.rect.centerx + 49, player.rect.top)
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
