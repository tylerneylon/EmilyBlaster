import pygame

class NineSlice:
    def __init__(self, image_filename, top_left, bottom_right):
        """
        Initializes the NineSlice object.
        
        Args:
            image_filename (str): Path to the 9-slice image file.
            top_left (tuple): (w, h) of the top-left fixed-size corner.
            bottom_right (tuple): (w, h) of the bottom-right fixed-size corner.
        """
        # Load image with alpha support
        self.image = pygame.image.load(image_filename).convert_alpha()

        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()

        self.top_left = top_left
        self.bottom_right = bottom_right

        # Margins for slicing
        self.left, self.top = top_left
        self.right, self.bottom = bottom_right

        # For convenience, set the minimum width and height.
        self.minwidth  = self.image_width
        self.minheight = self.image_height

    def draw(self, surface, x, y, width, height):
        """
        Draws the 9-slice scaled image on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on.
            x (int): X-coordinate for the top-left corner.
            y (int): Y-coordinate for the top-left corner.
            width (int): Target width of the rendered image.
            height (int): Target height of the rendered image.
        """
        dst_w  = max(width , self.minwidth)
        dst_h = max(height, self.minheight)

        # Define some shorthands to keep the code below more compact.
        ell, r = self.left, self.right
        t, b   = self.top,  self.bottom
        w, h   = self.image_width, self.image_height

        # Define regions of the original image
        corners = {
            "top_left":     self.image.subsurface((0,     0,     ell, t)),
            "top_right":    self.image.subsurface((w - r, 0,     r,   t)),
            "bottom_left":  self.image.subsurface((0,     h - b, ell, b)),
            "bottom_right": self.image.subsurface((w - r, h - b, r,   b))
        }

        edges = {
            "top":    self.image.subsurface((ell,   0,     w - ell - r, t)),
            "bottom": self.image.subsurface((ell,   h - b, w - ell - r, b)),
            "left":   self.image.subsurface((0,     t,     ell, h - t - b)),
            "right":  self.image.subsurface((w - r, t,     r,   h - t - b)),
        }

        center = self.image.subsurface((ell, t, w - ell - r, h - t - b))

        # Calculate scaled sizes
        scaled_parts = {
            "top": pygame.transform.scale(
                edges["top"],
                (dst_w - ell - r, t)
            ),
            "bottom": pygame.transform.scale(
                edges["bottom"],
                (dst_w - ell - r, b)
            ),
            "left": pygame.transform.scale(
                edges["left"],
                (ell, dst_h - t - b)
            ),
            "right": pygame.transform.scale(
                edges["right"],
                (r, dst_h - t - b)
            ),
            "center": pygame.transform.scale(
                center,
                (dst_w - ell - r, dst_h - t - b)
            ),
        }

        # Set up a few x, y pairs for convenience.
        # These go from top-left over to bottom-right.
        x1, y1 = x, y
        x2, y2 = x + ell, y + t
        x3, y3 = x + dst_w - r, y + dst_h - b

        # Blit the corners.
        surface.blit(corners["top_left"],     (x1, y1))
        surface.blit(corners["top_right"],    (x3, y1))
        surface.blit(corners["bottom_left"],  (x1, y3))
        surface.blit(corners["bottom_right"], (x3, y3))

        # Blit the edges.
        surface.blit(scaled_parts["top"],    (x2, y1))
        surface.blit(scaled_parts["bottom"], (x2, y3))
        surface.blit(scaled_parts["left"],   (x1, y2))
        surface.blit(scaled_parts["right"],  (x3, y2))

        # Blit the center.
        surface.blit(scaled_parts["center"], (x2, y2))
