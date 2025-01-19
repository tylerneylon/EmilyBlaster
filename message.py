
# ______________________________________________________________________
# Imports

import pygame

import fonts
import screen_setup
from nineslice import NineSlice
from screen_setup import screen_scale


# ______________________________________________________________________
# Public interface

class Message(pygame.sprite.Sprite):
    def __init__(self, title, text, x, y):
        super().__init__()

        scale_by = screen_setup.scale_up

        color = (50, 30, 10)

        msg_box = NineSlice('message_box_1.png', (54, 41), (61, 48), scale_by)
        text_srf, text_w, text_h = fonts.make_text_surface(
                fonts.main_font, text, color
        )
        title_srf, title_w, title_h = fonts.make_text_surface(
                fonts.nice_font, title, color
        )
        pad_w, pad_h = screen_scale(40), screen_scale(40)
        v_skip = screen_scale(40)
        w = max(max(title_w, text_w) + 2 * pad_w, msg_box.minwidth)
        h = max(title_h + v_skip + text_h + 2 * pad_h, msg_box.minheight)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        msg_box.draw(self.image, 0, 0, w, h)
        self.image.blit(title_srf, ((w - title_w) // 2, pad_h))
        self.image.blit(text_srf, ((w - text_w) // 2, pad_h + text_h + v_skip))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

