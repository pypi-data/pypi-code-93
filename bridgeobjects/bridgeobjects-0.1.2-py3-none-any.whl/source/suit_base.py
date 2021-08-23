"""A base class for bridgeobjects suits and denominations."""

__all__ = ['SuitBase']


class SuitBase(object):
    """
    A base object for the bridgeobjects Suit and Denominations classes.

    Parameters
    name: (str) suit or denomination's name

    Example
    -------
        suit = Suit("S")

    A SuitBase has a short name, a long name and a ranking.
    The SuitBases include no trumps. They are identified
    as major, minor, a suit or no trumps.

    The rank of a SuitBase is 0 for clubs, 1 for diamonds up to 4 for no trumps.
    SuitBases can be compared based on their rank:

    Example
    -------
        assert Suit('S') >= Suit('H')
    """

    #: valid names
    SHORT_NAMES = ['C', 'D', 'H', 'S']

    #: full names
    FULL_NAMES = ['clubs', 'diamonds', 'hearts', 'spades']

    MINORS = [True, True, False, False, False]
    MAJORS = [False, False, True, True, False]

    def __init__(self, name: str):
        if name:
            if not isinstance(name, str):
                raise TypeError('Suit name must be a string')
            if name not in self.SHORT_NAMES:
                raise ValueError(f'Invalid denomination {name}')
            self._name = name
            self._rank = self.SHORT_NAMES.index(self._name)
            self._full_name = self.FULL_NAMES[self._rank]
            self._is_major = self.MAJORS[self._rank]
            self._is_minor = self.MINORS[self._rank]
            self._is_no_trumps = self._name == 'NT'
            self._is_suit = self._is_major or self._is_minor
            self._game_level = self._get_game_level()
        else:
            self._name = ''
            self._full_name = ''
            self._rank = -1
            self._is_major = False
            self._is_minor = False
            self._is_suit = False
            self._game_level = 0
            self._is_no_trumps = False

    def __eq__(self, other) -> bool:
        if not other or not isinstance(other, SuitBase):
            return False
        if self._name == other.name:
            return True
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other) -> bool:
        if self._rank > other.rank:
            return True
        return False

    def __ge__(self, other) -> bool:
        if self._rank >= other.rank:
            return True
        return False

    def __lt__(self, other) -> bool:
        if self._rank < other.rank:
            return True
        return False

    def __le__(self, other) -> bool:
        if self._rank <= other.rank:
            return True
        return False

    def __hash__(self):
        """Return a hash value for the suit."""
        # Needed because we build a dict  of suit lengths with the suit as a key
        return hash((self.name, self.name))

    @property
    def name(self) -> str:
        """Returns the single character name of the suit as a string (e.g. 'S' or 'D')."""
        return self._name

    @property
    def full_name(self) -> str:
        """Returns the full name of the suit as a string (e.g. 'spades' or 'diamonds')."""
        return self._full_name

    @property
    def rank(self) -> int:
        """Returns the rank of the suit as an integer (e.g. 0 for 'S' or 2 for 'D')."""
        return self._rank

    @property
    def is_suit(self) -> bool:
        """Returns True if the suit is a suit, otherwise False."""
        return self._is_suit

    @property
    def is_major(self) -> bool:
        """Returns True if the suit is a major suit, otherwise False."""
        return self._is_major

    @property
    def is_minor(self) -> bool:
        """Returns True if the suit is a minor suit, otherwise False."""
        return self._is_minor

    @property
    def is_no_trumps(self) -> bool:
        """Returns True if the suit is a minor suit, otherwise False."""
        return self._is_no_trumps

    @property
    def is_nt(self) -> bool:
        """Returns True if the suit is a minor suit, otherwise False."""
        return self._is_no_trumps

    @property
    def game_level(self) -> int:
        """Returns the game level for the suit."""
        return self._game_level

    def _get_game_level(self) -> int:
        """Derive and return the game level for the suit."""
        if self._is_no_trumps:
            return 3
        elif self.is_major:
            return 4
        elif self.is_minor:
            return 5
        raise AttributeError('No value returned for game level')
