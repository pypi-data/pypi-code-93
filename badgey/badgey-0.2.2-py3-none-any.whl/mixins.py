class RangedBadgeMixin:
    """ This mixin defines a ranged badge. I.e. a badge that can have different
    states (e.g. 20%, 30%, 50%) and it associates a colormap to those values
    """

    @property
    def right_color(self):
        return self.color_map.color(self.value)
