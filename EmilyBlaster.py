''' EmilyBlaster.py

    This is a pixel art retro game based on the description of Sadie Green's
    first college-made game in the book Tomorrow, and Tomorrow, and Tomorrow by
    Gabrielle Zevin.
'''


# ______________________________________________________________________
# Imports

import math
import random

import pygame

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
TRANSPARENT = (0, 0, 0, 0)

# Game settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 10
PLAYER_SPEED = 7

BULLET_WIDTH = 9
BULLET_HEIGHT = 13
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

# Load and scale background image
background_image = pygame.image.load('tombstone_bg.png')
bg_width, bg_height = background_image.get_size()
scale_factor = max(SCREEN_WIDTH / bg_width, SCREEN_HEIGHT / bg_height)
new_size = (int(bg_width * scale_factor), int(bg_height * scale_factor))
background_image = pygame.transform.scale(background_image, new_size)

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
        w, h = BULLET_WIDTH, BULLET_HEIGHT
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        
        pad = 2
        pygame.draw.rect(
                self.image, WHITE,
                (0, 0, w, h),
                border_radius=3
        )
        pygame.draw.rect(
                self.image, BLACK,
                (pad, pad, w - 2 * pad, h - 2 * pad),
                border_radius=3
        )

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -BULLET_SPEED

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

class Blotch(pygame.sprite.Sprite):
    def __init__(self, x, y):
        ''' x, y are the center coordinates. '''
        super().__init__()
        self.image = pygame.image.load('ink_blotch_2.png')
        self.image = pygame.transform.rotate(
                self.image, random.randint(-50, 50)
        )
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

TOP_MARGIN = 35
BOTTOM_MARGIN = 100

# A class to assist with word tile movements
class WordPaths:
    def __init__(self, poem):
        self.poem = poem
        self.substrings = self._breakdown_poem()

        # Determine the path metrics.
        widest_tile = self._compute_widest_tile()
        row_skip = (SCREEN_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN) // 11
        top_path_y = TOP_MARGIN + row_skip // 2
        self._determine_paths(widest_tile, row_skip, top_path_y)

        # Compute where each tile should begin.
        self._initialize_tile_positions()

    def _compute_widest_tile(self):
        self.tile_offsets = []
        self.tile_widths  = []
        widest = 0
        for s in self.substrings:
            e = Enemy(0, 0, 0, s)
            r = e.image.get_rect()
            self.tile_offsets.append((-r.width // 2, -r.height // 2))
            self.tile_widths.append(r.width)
            widest = max(widest, r.width)
        return widest

    def _breakdown_poem(self):
        lines = self.poem.split('\n')
        return [
                word
                for line in lines
                for word in line.split()
        ]

    def _determine_paths(self, widest_tile, row_skip, top_path_y):
        self.paths = []
        scr_w = SCREEN_WIDTH
        w = widest_tile // 2
        for path_idx in range(2):

            def refl(x, i=-1):
                if path_idx == 0 and i > 0:
                    x = x - widest_tile if x == scr_w - w else x
                if path_idx == 1:
                    x = scr_w - x
                    if i < 2:
                        x = x + widest_tile if x == w else x
                return x

            path = []  # This will be a set of (x, y) points (tuples).
            offscreen_x = -w - 10
            x = refl(offscreen_x)
            y = top_path_y + 2 * row_skip * path_idx
            for i in range(3):
                path.append((x, y))
                x = refl(scr_w - w, i)

                # Special case: End early if this is the last row.
                if path_idx == 1 and i == 2:
                    x = offscreen_x
                    path.append((x, y))
                    break

                path.append((x, y))
                y += row_skip
                path.append((x, y))
                x = refl(w, i) if i < 2 else refl(offscreen_x, i)
                path.append((x, y))
                y += 3 * row_skip
            self.paths.append(path)
            # print(f'path {path_idx}:', path)

    def _initialize_tile_positions(self):
        ''' This will set up the self.tile_start[] list. '''
        pad = 60
        self.tile_start = []
        t = [0, 0]
        prev_w = [0, 0]
        for i, width in enumerate(self.tile_widths):
            idx = i % 2
            s = t[idx] - (prev_w[idx] + width) // 2 - pad
            self.tile_start.append(s)
            t[idx] = s
            prev_w[idx] = width

    def get_tile_pos(self, tile_idx, t):
        ''' Return the top-left x, y coordinates of the given tile. '''
        speed = 170  # This is in pixels per second.
        speed = 300
        pos  = max(0, self.tile_start[tile_idx] + t / 1000 * speed)
        d    = 0
        path = self.paths[tile_idx % 2]
        x, y = path[0]
        dx, dy = self.tile_offsets[tile_idx]  # To move from center to topleft.
        for x2, y2 in path[1:]:
            dist = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)
            if d + dist > pos:
                perc = (pos - d) / dist
                x += (x2 - x) * perc
                y += (y2 - y) * perc
                return x + dx, y + dy
            d += dist
            x, y = x2, y2
        # If we get here, then the tile is off the screen.
        # We'll return the path's final endpoint.
        x, y = path[-1]
        return x + dx, y + dy

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_idx, s):
        super().__init__()
        self.tile_idx = tile_idx
        bg_nineslice = NineSlice('word_box_6.png', (52, 27), (55, 29))
        text_surface = main_font.render(s, True, (80, 60, 30))
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
        t = pygame.time.get_ticks()
        x, y = word_paths.get_tile_pos(self.tile_idx, t)
        self.rect.x = x
        self.rect.y = y
        if False:
            self.rect.x += self.speed_x
            if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
                self.speed_x *= -1

class Poem(pygame.sprite.Sprite):
    def __init__(self, poem, delta_x=0):
        super().__init__()

        self.interline_skip = 16
        p = self.padding = 10

        # Quietly render the text just to learn the sizing.
        self.n = n = self._get_num_words(poem)
        buff = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.render_rich_text(buff, poem, [WHITE] * n, 255, (0, 0), do_blit=False)
        w, h = self.text_w, self.text_h
        w, h = w + 2 * p, h + 2 * p

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # Initially render to a buffer image that we can make translucent.
        buff = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(buff, (128, 128, 128, 70), (0, 0, w, h), border_radius=p)
        self.render_rich_text(buff, poem, [BLACK] * n, 255, (p + 2, p    ))
        self.render_rich_text(buff, poem, [WHITE] * n, 255, (p    , p + 2))
        self.render_rich_text(buff, poem, [GRAY]  * n, 255, (p + 1, p + 1))
        buff.set_alpha(140)

        self.image.blit(buff, (0, 0))

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2 + delta_x
        self.rect.centery = SCREEN_HEIGHT // 2

        self.poem = poem

    def _get_num_words(self, poem):
        return len([
            w
            for line in poem
            for w in line.split()
        ])

    def render_string(self, s, color, alpha, pos):
        text_surface = main_font.render(s, False, color)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(topleft=pos)
        self.image.blit(text_surface, text_rect)

    def render_rich_text(
            self, dst, text, word_colors, alpha, position, do_blit=True):
        lines = text.split('\n')
        w_idx = 0
        pos = list(position)
        w, h = 0, 0
        for line in lines:
            for word in line.split():
                color = word_colors[w_idx]
                text_surface = main_font.render(word, False, color)
                text_surface.set_alpha(alpha)
                text_rect = text_surface.get_rect(topleft=pos)
                if do_blit and (color != TRANSPARENT):
                    dst.blit(text_surface, text_rect)
                w_idx += 1
                w = max(w, pos[0] + text_surface.get_width())
                pos[0] += text_surface.get_width() + 10
            h = max(h, pos[1] + text_surface.get_height())
            pos[0] = position[0]
            pos[1] += text_surface.get_height() + self.interline_skip
        self.text_w = w
        self.text_h = h

    def render_multiline_text(self, text, color, alpha, position):
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

    def highlight_word_idx(self, word_idx):
        main_color = (200, 190, 185)
        for i, w_color in enumerate([BLACK, BLACK, main_color]):
            j = (i + 2) % 3
            word_colors = [TRANSPARENT] * self.n
            word_colors[word_idx] = w_color
            p = self.padding
            x, y = p + j, p + 2 - j
            self.render_rich_text(
                    self.image, self.poem, word_colors, 255, (x, y)
            )


# ______________________________________________________________________
# Main game code

# Initialize sprites
player = Player()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
blotches = pygame.sprite.Group()
poem = Poem(poem1, delta_x=-150)

word_paths = WordPaths(poem1)

# Create enemies
for i, s in enumerate(word_paths.substrings):
    x, y = word_paths.get_tile_pos(i, 0)
    enemy = Enemy(x, y, i, s)
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
                bullet = Bullet(player.rect.centerx + 49, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

    # Update sprites
    all_sprites.update()

    # Check for collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    if len(hits) > 0:
        splat.play()
    gone_bullets = set()
    for hit, bullet_list in hits.items():
        score += 1
        poem.highlight_word_idx(hit.tile_idx)
        gone_bullets |= set(bullet_list)
        if False:
            # Spawn a new enemy at a random position
            x = random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH)
            y = random.randint(20, 200)
            enemy = Enemy(x, y)
            enemies.add(enemy)
            all_sprites.add(enemy)
    for b in gone_bullets:
        x, y = b.rect.centerx, b.rect.centery
        blotch = Blotch(b.rect.centerx, b.rect.centery)
        blotches.add(blotch)

    # Draw everything
    bg_x = (SCREEN_WIDTH - background_image.get_width()) // 2
    bg_y = (SCREEN_HEIGHT - background_image.get_height()) // 2
    screen.blit(background_image, (bg_x, bg_y))
    screen.blit(poem.image, poem.rect)
    blotches.draw(screen)
    all_sprites.draw(screen)

    # Draw score
    score_text = main_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Refresh display
    pygame.display.flip()

pygame.quit()
