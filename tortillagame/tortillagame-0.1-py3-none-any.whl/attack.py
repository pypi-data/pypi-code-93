from tortilla.hexagon import Hexagon
from tortilla.entities import *


class Attack:
    @staticmethod
    def execute(start_hexagon: Hexagon, end_hexagon: Hexagon):
        attacker: Ship = start_hexagon.entity

        if end_hexagon.entity \
                and start_hexagon.entity.owner is not end_hexagon.entity.owner \
                and attacker.move_points >= 3:

            receiver: Ship = end_hexagon.entity

            receiver.health_points -= attacker.weapon_damage
            if receiver.health_points <= 0:
                receiver.health_points = 0
                receiver.is_killed = True
                end_hexagon.entity = None

            attacker.move_points = 0
            return True
        else:
            return False
