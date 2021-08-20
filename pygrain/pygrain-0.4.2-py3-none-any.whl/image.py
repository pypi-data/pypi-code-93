from .component import Component
from .util import show_image
import pygame


class Image(Component):
    def __init__(self, parent, filepath, **kwargs):
        super().__init__(parent, **kwargs)
        self.filepath = filepath
        image = pygame.image.load(filepath).convert()
        self.set_property('width', image.get_width())
        self.set_property('height', image.get_height())

    def draw(self, screen):
        super().draw(screen)
        filepath = self.get_property('filepath')
        image = pygame.image.load(filepath).convert()
        screen.blit(image, (self.get_abs_x(), self.get_abs_y()))
