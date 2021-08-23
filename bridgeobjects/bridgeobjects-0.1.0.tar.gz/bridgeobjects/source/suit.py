"""Suit classes for bridgeobjects."""

from .suit_base import SuitBase

__all__ = ['Suit', 'Clubs', 'Diamonds',  'Hearts', 'Spades']


class Suit(SuitBase):
    """
    The suit object for the bridgeobjects module.
    Suits apply to cards, Denominations to calls.

    Parameters
    ----------
    name: (str) suit's name

    Example
    -------
        suit = Suit("C")

        A suit has a short name, a long name and a ranking.
        The suits include no trumps. They are identified
        as major, minor.

        The rank of a suit is 0 for clubs, 1 for diamonds up to 3 for spades.
        Suits can be compared based on their rank:

    Example
    -------
        assert Suit('S') >= Suit('H')
    """

    def __init__(self, short_name: str):
        super().__init__(short_name)

    def __repr__(self) -> str:
        return f'Suit("{self._name}")'

    def __str__(self) -> str:
        return f'Suit("{self._name}")'


class Spades(Suit):
    """
        The spades suit object for the bridgeobjects module.

        A subclass of Suit.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('S', *args, **kwargs)


class Hearts(Suit):
    """
        The hearts suit object for the bridgeobjects module.

        A subclass of Suit.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('H', *args, **kwargs)


class Diamonds(Suit):
    """
        The diamonds suit object for the bridgeobjects module.

        A subclass of Suit.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('D', *args, **kwargs)


class Clubs(Suit):
    """
        The clubs suit object for the bridgeobjects module.

        A subclass of Suit.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('C', *args, **kwargs)
