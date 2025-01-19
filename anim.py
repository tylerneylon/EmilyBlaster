import pygame

# This is a list of (timestamp, fn) pairs.
# This module keeps the pairs sorted.
# As soon as each `timestamp` value is met or passed, the associated
# function is called, and the pair is removed from `actions`.
actions = []

def call_after_delay(fn, delay_seconds):
    now = pygame.time.get_ticks()
    deadline = now + delay_seconds * 1_000
    actions.append((deadline, fn))
    actions.sort()

def handle_anim_events():
    now = pygame.time.get_ticks()
    while len(actions) and now >= actions[0][0]:
        fn = actions[0][1]
        fn()
        del actions[0]
