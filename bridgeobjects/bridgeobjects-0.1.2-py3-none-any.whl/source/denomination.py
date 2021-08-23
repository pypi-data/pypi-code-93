"""Provide various suit classes for bridgeobjects."""

__all__ = ['Denomination', 'Clubs', 'Diamonds',  'Hearts', 'Spades', 'NoTrumps']

from .suit_base import SuitBase


class Denomination(SuitBase):
    """
    The denomination object for the bridgeobjects module.
    Denominations apply to calls, Suits to cards.

    Parameters
    ----------
    name: (str) denomination's name

    Example
    -------
        denomination = Denomination("NT")

    A denomination has a short name, a long name and a ranking.
    The denominations include no trumps. They are identified as major, minor, a suit or no trumps.

    The rank of a denomination is 0 for clubs, 1 for diamonds up to 4 for no trumps.
    Denominations can be compared based on their rank:

    Example
    -------
        assert Denomination('NT') >= Denomination('S')
    """

    #: short names
    SHORT_NAMES = [short_name for short_name in SuitBase.SHORT_NAMES]
    SHORT_NAMES.append('NT')

    #: full names
    FULL_NAMES = [full_name for full_name in SuitBase.FULL_NAMES]
    FULL_NAMES.append('no trumps')

    def __init__(self, short_name: str=''):
        super().__init__(short_name)
        if short_name:
            self._is_no_trumps = self._name == 'NT'
            self._is_suit = self._is_major or self._is_minor

    def __repr__(self) -> str:
        return f'Denomination("{self._name}")'

    def __str__(self) -> str:
        return f'Denomination("{self._name}")'

    @property
    def full_name(self) -> str:
        """Returns the full name of the denomination as a string (e.g. 'spades' or 'diamonds')."""
        return self._full_name


class Spades(Denomination):
    """
        The spades denomination object for the bridgeobjects module.

        A subclass of Denomination.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('S', *args, **kwargs)


class Hearts(Denomination):
    """
        The hearts denomination object for the bridgeobjects module.

        A subclass of Denomination.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('H', *args, **kwargs)


class Diamonds(Denomination):
    """
        The diamonds denomination object for the bridgeobjects module.

        A subclass of Denomination.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('D', *args, **kwargs)


class Clubs(Denomination):
    """
        The clubs denomination object for the bridgeobjects module.

        A subclass of Denomination.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('C', *args, **kwargs)


class NoTrumps(Denomination):
    """
        The NoTrumps denomination object for the bridgeobjects module.

        A subclass of Denomination.
    """
    def __init__(self, *args, **kwargs):
        super().__init__('NT', *args, **kwargs)
