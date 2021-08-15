from tortilla.move import Move
from tortilla.attack import Attack


class Strategy:
    @staticmethod
    def update_k_left(model):
        pass

    @staticmethod
    def update_k_up(model):
        pass

    @staticmethod
    def update_k_right(model):
        pass

    @staticmethod
    def update_k_down(model):
        pass

    @staticmethod
    def update_k_a(model):
        pass

    @staticmethod
    def update_k_escape(model):
        pass

    @staticmethod
    def update_k_v(model):
        pass

    @staticmethod
    def update_k_space(model):
        pass


class SelectStrategy(Strategy):
    @staticmethod
    def update_k_left(model):
        if model.field.directed_hexagon.neighbors[3]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[3]
        # x, y = model.field.directed_hexagon
        #if y - 1 >= 0:
        #    model.field.directed_hexagon = x, y - 1
        return 'select'

    @staticmethod
    def update_k_up(model):
        if model.field.directed_hexagon.neighbors[2]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[2]
        return 'select'

    @staticmethod
    def update_k_right(model):
        if model.field.directed_hexagon.neighbors[0]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[0]
        return 'select'

    @staticmethod
    def update_k_down(model):
        if model.field.directed_hexagon.neighbors[5]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[5]
        return 'select'

    @staticmethod
    def update_k_a(model):
        if model.field.directed_hexagon.entity:
            entity = model.field.directed_hexagon.entity
            model.field.selected_hexagon = model.field.directed_hexagon
            if entity.owner is model.current_player:
                model.field.reachable_hexagons = model.field.selected_hexagon.neighbors
                return 'move'
            else:
                return 'overview'
        return 'select'

    @staticmethod
    def update_k_space(model):
        model.set_next_turn()
        return 'select'


class MoveStrategy(Strategy):
    @staticmethod
    def update_k_left(model):
        if model.field.directed_hexagon.neighbors[3]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[3]
        return 'move'

    @staticmethod
    def update_k_up(model):
        if model.field.directed_hexagon.neighbors[2]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[2]
        return 'move'

    @staticmethod
    def update_k_right(model):
        if model.field.directed_hexagon.neighbors[0]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[0]
        return 'move'

    @staticmethod
    def update_k_down(model):
        if model.field.directed_hexagon.neighbors[5]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[5]
        return 'move'

    @staticmethod
    def update_k_a(model):
        if Move.execute(model.field.selected_hexagon, model.field.directed_hexagon):
            model.field.selected_hexagon = None
            model.field.reachable_hexagons = None
            return 'select'
        else:
            return 'move'

    @staticmethod
    def update_k_escape(model):
        model.field.selected_hexagon = None
        model.field.reachable_hexagons = None
        return 'select'

    @staticmethod
    def update_k_v(model):
        model.field.reachable_hexagons = None
        return 'attack'


class AttackStrategy(Strategy):
    @staticmethod
    def update_k_left(model):
        if model.field.directed_hexagon.neighbors[3]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[3]
        return 'attack'

    @staticmethod
    def update_k_up(model):
        if model.field.directed_hexagon.neighbors[2]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[2]
        return 'attack'

    @staticmethod
    def update_k_right(model):
        if model.field.directed_hexagon.neighbors[0]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[0]
        return 'attack'

    @staticmethod
    def update_k_down(model):
        if model.field.directed_hexagon.neighbors[5]:
            model.field.directed_hexagon = model.field.directed_hexagon.neighbors[5]
        return 'attack'

    @staticmethod
    def update_k_a(model):
        if Attack.execute(model.field.selected_hexagon, model.field.directed_hexagon):
            model.field.selected_hexagon = None
            return 'select'
        else:
            return 'attack'

    @staticmethod
    def update_k_escape(model):
        model.field.selected_hexagon = None
        return 'select'

    @staticmethod
    def update_k_v(model):
        return 'move'


class OverviewStrategy(Strategy):
    @staticmethod
    def update_k_escape(model):
        model.field.selected_hexagon = None
        return 'select'
