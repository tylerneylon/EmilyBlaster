# ______________________________________________________________________
# Imports

import sys

import pygame


# ______________________________________________________________________
# Globals and constants

scale_up = None

# Screen dimensions
screen_w = 1024
screen_h =  768


# ______________________________________________________________________
# Public interface

def init():
    global scale_up, screen_w, screen_h
    fullscreen = '--fullscreen' in sys.argv
    if fullscreen:
        screen = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=True
        )
        screen_w, screen_h = screen.get_size()
        sw = screen_w / 768
        sh = screen_h / 1024
        a, b = min(sw, sh), max(sw, sh)
        a_weight = 0.75
        scale_up = a_weight * a + (1 - a_weight) * b
    else:
        screen = pygame.display.set_mode(
                (screen_w, screen_h), pygame.DOUBLEBUF, vsync=True
        )
        scale_up = 1
    return screen, scale_up

def screen_scale(x):
    return int(x * scale_up)

