import abc

from matplotlib.cm import get_cmap
from matplotlib.colors import to_hex


class ColorMap(metaclass=abc.ABCMeta):
    """ A :class:`ColorMap`, same as for :module:`matplotlib.cm`, is a callable
    that given a value between [0, 1], returns the corresponding color. The
    only difference is that the color is returned as an hexadecimal string
    """

    reverse: bool = False

    @classmethod
    def color(cls, value: float) -> str:
        if cls.reverse:
            value = 1 - value

        return cls.get_color(value)

    @abc.abstractclassmethod
    def get_color(cls, value: float) -> str:
        raise NotImplementedError


class StandardColorMap(ColorMap):
    """ This is a standard :class:`ColorMap` providing 3 levels of thresholds

        * `value < left_threshold`: bad_color
        * `left_threshold <= value < right_threshold`: average_color
        * `value >= right_threshold`: good_color

        Attributes
        ---------
        left_threshold
            The value of the left threshold
        right_threshold
            The value of the right threshold
        bad_color
            The color for bad (default to: #A32842)
        average_color
            The color for average status (default to: #EA8C55)
        good_color
            The color for good status (default to: #00CC99)



    >>> cmap = StandardColorMap()
    >>> assert cmap.left_threshold > cmap.right_treshold
    >>> assert cmap.bad_color == "#a32842"
    >>> assert cmap.average_color == "#ea8c55"
    >>> assert cmap.good_color == "#00cc99"
    >>> assert cmap(0) == cmap.bad_color
    >>> assert cmap(0.5) == cmap.average_color
    >>> assert cmap(1) == cmap.good_color
    """

    left_threshold: float = 0.5
    right_treshold: float = 0.9

    bad_color = "#a32842"
    average_color = "#ea8c55"
    good_color = "#00cc99"

    @classmethod
    def get_color(cls, value: float) -> str:
        if value < cls.left_threshold:
            return cls.bad_color
        elif value > cls.right_treshold:
            return cls.good_color
        else:
            return cls.average_color


class DivergingColorMap(ColorMap):
    """ This colormap uses :module`matplotlib.cm` `RdYlGn` diverging map
    """

    cmap = get_cmap("RdYlGn")

    @classmethod
    def get_color(cls, value: float) -> str:
        return to_hex(cls.cmap(value))
