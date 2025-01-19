''' fonts.py

    A centralized place for loading and working with fonts.
'''

import pygame

from screen_setup import screen_scale


# ______________________________________________________________________
# Globals and constants

main_font = None
nice_font = None


# ______________________________________________________________________
# Public interface

def init():
    global main_font, nice_font
    if main_font is not None:
        return
    main_font = pygame.font.Font('dogicapixel.ttf', screen_scale(20))
    nice_font = pygame.font.Font('alagard.ttf', screen_scale(30))
