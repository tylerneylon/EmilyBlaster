
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

        # TODO: Determine how large the box needs to be for the title & text.
        msg_box = NineSlice('message_box_1.png', (54, 41), (61, 48), scale_by)
        text_surface = fonts.main_font.render(text, True, (255, 255, 255))
        text_w, text_h = text_surface.get_width(), text_surface.get_height()
        pad_w, pad_h = screen_scale(40), screen_scale(25)
        w = max(text_w + pad_w, msg_box.minwidth)
        h = max(text_h + pad_h, msg_box.minheight)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        msg_box.draw(self.image, 0, 0, w, h)
        self.image.blit(text_surface, ((w - text_w) // 2, (h - text_h) // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

