"""The call object for the bridgeobjects module."""

from .denomination import Denomination
from .constants import CALLS

__all__ = ['Call']


class Call(object):
    """
    The call object for the bridgeobjects module.


    Parameters
    ----------
    name: (str) the call's name

    Example
    -------
        call = Call("3NT")

    A call has a short name and a level.
    It is also identified (if appropriate) as either major, minor or no trumps.

    A call other than Pass, Double or Redouble is a 'value call'.

    Calls can be compared based on their level and denomination:

    Example
    -------
        assert Call('1NT') > Call('1S')
    """

    def __init__(self, name: str=''):
        if name and name.replace('X', '') not in CALLS:
            raise ValueError(f'{name} is not a Call')
        self._name = name
        self._level = 0
        self._denomination = Denomination('')
        self._is_major = False
        self._is_minor = False
        self._is_no_trumps = False
        self._is_value_call = False
        self._is_suit_call = False
        self._is_pass = name == 'P'
        self._is_double = name == 'D'
        self._is_redouble = name == 'R'
        if name:
            if name[1:] in Denomination.SHORT_NAMES:
                if len(name) <= 3:
                    self._denomination = Denomination(name[1:])
                    self._is_major = self._denomination.is_major
                    self._is_minor = self._denomination.is_minor
                    self._is_suit_call = self._is_major or self._is_minor
                    self._is_no_trumps = not self._is_suit_call
                    self._is_value_call = self._is_suit_call or self._is_no_trumps
                    self._level = int(name[0])
        self._is_game = self._set_is_game()
        self.image = None
        self.bitmap = None

    def __eq__(self, other) -> bool:
        if not other:
            return False
        if self._name == other.name:
            return True
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other) -> bool:
        if self._level > other.level:
            return True
        if self._level == other.level:
            if self._denomination > other.denomination:
                return True
        return False

    def __ge__(self, other) -> bool:
        if self._level > other.level:
            return True
        if self._level == other.level:
            if self._denomination >= other.denomination:
                return True
        return False

    def __lt__(self, other) -> bool:
        if self._level < other.level:
            return True
        if self._level == other.level:
            if self._denomination < other.denomination:
                return True
        return False

    def __le__(self, other) -> bool:
        if self._level < other.level:
            return True
        if self._level == other.level:
            if self._denomination <= other.denomination:
                return True
        return False

    def __repr__(self) -> str:
        return f'Call("{self._name}")'

    def __str__(self) -> str:
        return f'Call("{self._name}")'

    @property
    def name(self) -> str:
        """Returns name of the call as a string."""
        return self._name

    @property
    def denomination(self) -> Denomination:
        """Returns the denomination of the call as a Denomination object."""
        return self._denomination

    @property
    def level(self) -> int:
        """Returns the level of the call as an integer (e.g. 1 for '1NT', 3 for '3S')."""
        return self._level

    @property
    def is_suit_call(self) -> bool:
        """Returns True if the call is a suit call, otherwise False."""
        return self._is_suit_call

    @property
    def is_major(self) -> bool:
        """Returns True if the call suit is a major suit, otherwise False."""
        return self._is_major

    @property
    def is_minor(self) -> bool:
        """Returns True if the call suit is a minor suit, otherwise False."""
        return self._is_minor

    @property
    def is_no_trumps(self) -> bool:
        """Returns True if the call is no trumps, otherwise False."""
        return self._is_no_trumps

    @property
    def is_nt(self) -> bool:
        """Returns True if the call is no trumps, otherwise False."""
        return self._is_no_trumps

    @property
    def is_value_call(self) -> bool:
        """Returns True if the call no trumps, otherwise False."""
        return self._is_value_call

    @property
    def is_pass(self) -> bool:
        """Return True if the call is Pass."""
        return self._is_pass

    @property
    def is_double(self) -> bool:
        """Return True if the call is Double."""
        return self._is_double

    @property
    def is_redouble(self) -> bool:
        """Return True if the call is Redouble."""
        return self._is_redouble

    @property
    def is_pass_or_double(self) -> bool:
        """Return True if the call is Pass or Double."""
        return self._is_pass or self._is_double

    @property
    def is_game(self) -> bool:
        """Return True if the call is at game level or above."""
        return self._is_game

    def _set_is_game(self) -> bool:
        """Return True if bid is at or above game level."""
        if self._is_no_trumps and self._level >= 3:
            return True
        elif self._is_major and self._level >= 4:
            return True
        elif self._is_minor and self._level >= 5:
            return True
        else:
            return False
