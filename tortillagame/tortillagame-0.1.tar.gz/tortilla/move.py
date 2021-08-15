from tortilla.hexagon import Hexagon
from tortilla.entities import *


class Move:
    @staticmethod
    def execute(start_hexagon: Hexagon, end_hexagon: Hexagon):
        entity: Movable = start_hexagon.entity
        if end_hexagon in start_hexagon.neighbors and not end_hexagon.entity and entity.move_points > 0:
            entity.move_points -= 1
            end_hexagon.entity = start_hexagon.entity
            start_hexagon.entity = None
            return True
        return False
