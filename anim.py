''' anim.py

    An interface to help us work with events and animations.
'''


# ______________________________________________________________________
# Imports

import pygame
import weakref

import numpy as np


# ______________________________________________________________________
# Delayed-Call System

actions = []  # list of (timestamp, fn)

def call_after_delay(fn, delay_seconds):
    now = pygame.time.get_ticks()
    deadline = now + int(delay_seconds * 1000)
    actions.append((deadline, fn))
    actions.sort(key=lambda x: x[0])


# ______________________________________________________________________
# Per-Frame Hook for All AnimSprites

_active_sprites = weakref.WeakSet()

def handle_anim_events():
    """
    1) Process any scheduled one-shot actions (e.g. call_after_delay).
    2) Update all AnimSprite instances exactly once this frame.
    """
    now = pygame.time.get_ticks()

    # 1) Handle any delayed-call actions
    while actions and now >= actions[0][0]:
        _, fn = actions[0]
        fn()
        del actions[0]

    # 2) Update all active AnimSprites
    for sprite in list(_active_sprites):
        sprite.update(now)


# ______________________________________________________________________
# AnimSprite Class

class AnimSprite(pygame.sprite.Sprite):
    def __init__(self, base_surface):
        super().__init__()
        self.base_surface = base_surface
        self.image = self.base_surface.copy()
        self.base_rect = self.rect = self.image.get_rect()

        # A list of "chains." Each chain is a list of callables (animation fns).
        # On each frame, we call the first callable of each chain; if it returns
        # False, we pop it. If the chain is empty, we remove the chain entirely.
        self.fn_chains = []

        # For chaining “.then(fn)” we store the most recently created chain.
        self._last_chain = None

        # If we start indefinite flashing, we keep its chain reference.
        self._flash_chain = None

        _active_sprites.add(self)

    # __________________________________________________________________
    # Slide

    def slide(self, delta, duration=1.0):
        """
        Slide the sprite by `delta` (x, y) over `duration` seconds.
        """
        start_time = pygame.time.get_ticks()
        end_time = start_time + int(duration * 1000)
        start_pos = self.rect.topleft

        def slide_anim(now):
            now = min(now, end_time)
            ongoing = (now < end_time)

            elapsed = now - start_time
            if end_time > start_time:
                frac = elapsed / (end_time - start_time)
            else:
                frac = 1.0

            new_x = start_pos[0] + int(delta[0] * frac)
            new_y = start_pos[1] + int(delta[1] * frac)
            self.rect.topleft = (new_x, new_y)

            return ongoing

        chain = [slide_anim]
        self.fn_chains.append(chain)
        self._last_chain = chain
        return self

    # __________________________________________________________________
    # Flashing

    def start_flashing(self):
        """Begin indefinite flashing, if not already active."""
        if self._flash_chain is not None:
            return  # already flashing

        flash_start_time = pygame.time.get_ticks()
        cycle_duration = 1000  # ms

        def flash_anim(now):
            # T = 0..cycle_duration, we move "up" 0->0.8, then "down" 0.8->0
            elapsed = (now - flash_start_time) % cycle_duration
            half_cycle = cycle_duration / 2
            if elapsed <= half_cycle:
                factor = 0.8 * (elapsed / half_cycle)
            else:
                factor = 0.8 * (1 - (elapsed - half_cycle) / half_cycle)

            # Create an overlay surface with the desired alpha.
            alpha = int(factor * 255)
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, alpha))

            # Use the alpha mask from self.image.
            alpha_mask = pygame.surfarray.pixels_alpha(self.image)
            overlay_alpha = pygame.surfarray.pixels_alpha(overlay)
            overlay_alpha[:] = (
                    overlay_alpha * (alpha_mask.astype(np.float32) / 255)
            ).astype(np.uint8)
            # We need to delete these in order to unlock the surfaces.
            del alpha_mask
            del overlay_alpha

            # Blit the overlay onto self.image
            self.image.blit(overlay, (0, 0))

            return True  # never finishes on its own

        chain = [flash_anim]
        self.fn_chains.append(chain)
        self._flash_chain = chain

    def stop_flashing(self):
        """Stop indefinite flashing, if active."""
        if self._flash_chain in self.fn_chains:
            self.fn_chains.remove(self._flash_chain)
        self._flash_chain = None

    # __________________________________________________________________
    # Rotate

    def rotate(self, cycle_duration=0.5, stop_after_duration=1.5, center=None):
        """
        Rotate 360 degrees over `cycle_duration` seconds, stopping after
        `stop_after_duration` seconds. Keeps the final rotation.
        If `center` is None, rotate around the sprite's current center.
        Otherwise, rotate around (center.x, center.y) in local coordinates.
        """
        start_time = pygame.time.get_ticks()
        cycle_ms = cycle_duration * 1000
        end_time = start_time + stop_after_duration * 1000

        def rotate_anim(now):
            now = min(now, end_time)
            ongoing = (now < end_time)

            elapsed = now - start_time
            fraction = elapsed / cycle_ms if cycle_ms else 0
            angle = 360 * fraction

            rotated = pygame.transform.rotate(self.base_surface, angle)

            old_center = self.rect.center  # Keep world center if center=None.
            if center is None:
                self.image = rotated
                self.rect = self.image.get_rect(center=old_center)
            else:
                self.image = rotated
                self.rect = self.image.get_rect()
                # Shift so (center.x, center.y) stays where it was.
                dx = center[0] - self.rect.width // 2
                dy = center[1] - self.rect.height // 2
                self.rect.move_ip(dx, dy)

            return ongoing

        chain = [rotate_anim]
        self.fn_chains.append(chain)
        self._last_chain = chain
        return self

    # __________________________________________________________________
    # Fade

    def fade_out(self, duration=2.0):
        """Fade to transparent over `duration` seconds."""
        start_time = pygame.time.get_ticks()
        end_time = start_time + int(duration * 1000)

        def fade_anim(now):
            now = min(now, end_time)
            ongoing = (now < end_time)

            elapsed = now - start_time
            if end_time > start_time:
                frac = 1.0 - (elapsed / (end_time - start_time))
            else:
                frac = 1.0

            alpha_val = int(frac * 255)
            self.image.set_alpha(alpha_val)

            return ongoing

        chain = [fade_anim]
        self.fn_chains.append(chain)
        self._last_chain = chain
        return self

    # __________________________________________________________________
    # Chaining

    def then(self, fn):
        """
        Schedules `fn()` to run after the most recent process finishes.
        """
        if self._last_chain:
            def callback_anim(_now):
                fn()
                return False  # one-shot
            self._last_chain.append(callback_anim)
        return self

    # __________________________________________________________________
    # Main Update

    def update(self, now):
        """
        1) Reset self.image & self.rect to base each frame.
        2) For each chain (iterated in reverse so we can safely del empty ones):
           - Call the first function in that chain.
           - If it returns False, pop it. If empty, remove the chain.
        """

        self.image = self.base_surface.copy()
        self.rect = self.base_rect

        # Iterate backwards so we can safely delete from fn_chains in-place.
        for i in reversed(range(len(self.fn_chains))):
            chain = self.fn_chains[i]
            if not chain:
                del self.fn_chains[i]
                continue

            # Call the first anim function.
            keep_going = chain[0](now)
            if not keep_going:
                chain.pop(0)
                # If that was the only anim in the chain, remove the chain.
                if not chain:
                    del self.fn_chains[i]
