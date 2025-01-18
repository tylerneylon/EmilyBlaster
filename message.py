from nineslice import NineSlice
from screen import scale_up, screen_scale

# TODO: Factor out font loading so it only happens in one place.
main_font = pygame.font.Font('dogicapixel.ttf', screen_scale(20))
nice_font = pygame.font.Font('alagard.ttf', screen_scale(30))

class Message:
    def __init__(self, title, text, x, y, scale_by=1):

        # TODO: Determine how large the box needs to be for the title & text.
        NineSlice('message_box_1.png', (54, 41), (61, 48), scale_by)

