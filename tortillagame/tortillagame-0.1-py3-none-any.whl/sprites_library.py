from tortilla.constants import SCALE_FACTOR
from tortilla.extractor import ImageExtractor
from tortilla.entities import *


class SpritesLibrary:
    def __init__(self):
        self._extractor = ImageExtractor()
        self._ship_images = (
            self._extractor.extract_image("tortilla\\assets\\sprites\\ship_0.png", SCALE_FACTOR),
            self._extractor.extract_image("tortilla\\assets\\sprites\\ship_1.png", SCALE_FACTOR)
        )
        self._obstacle_images = (
            self._extractor.extract_image("tortilla\\assets\\sprites\\obstacle_0.png", SCALE_FACTOR),
        )

    def get_asset(self, entity):
        if issubclass(type(entity), Entity):
            if type(entity) == Ship:
                return self._ship_images[entity.owner.player_id]
            elif type(entity) == Obstacle:
                return self._obstacle_images[0]
            else:
                return None
