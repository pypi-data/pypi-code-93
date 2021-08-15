from tortilla.constants import *
from pygame import gfxdraw


class TextObjects:
    @staticmethod
    def execute(text, font: pygame.font, colour=BLACK) -> (pygame.Surface, pygame.Rect):
        text_surface = font.render(text, True, colour)
        return text_surface, text_surface.get_rect()


class DrawCircle:
    @staticmethod
    def execute(surface, x, y, radius, color):
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)
