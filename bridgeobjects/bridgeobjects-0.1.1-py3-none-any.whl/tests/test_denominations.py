"""A set of tests for the bridgeobjects Denomination class."""
from ..source.denomination import Denomination, Spades, Hearts, Diamonds, Clubs, NoTrumps

spades = Spades()
hearts = Hearts()
diamonds = Diamonds()
clubs = Clubs()
no_trumps = NoTrumps()


def test_denomination_name():
    """Ensure that the denomination name is correct."""
    assert spades.name == 'S'
    assert hearts.name == 'H'
    assert diamonds.name == 'D'
    assert clubs.name == 'C'
    assert no_trumps.name == 'NT'
    assert Denomination('').name == ''


def test_is_suit():
    """Ensure that the is_suit is correct."""
    assert clubs.is_suit
    assert not no_trumps.is_suit


def test_is_no_trumps():
    """Ensure that the is_no_trumps is correct."""
    assert not clubs.is_no_trumps
    assert no_trumps.is_no_trumps


def test_is_nt():
    """Ensure that the is_nt is correct."""
    assert not clubs.is_nt
    assert no_trumps.is_nt


def test_geme_level():
    """Ensure that the game level is correct."""
    assert clubs.game_level == 5
    assert diamonds.game_level == 5
    assert hearts.game_level == 4
    assert spades.game_level == 4
    assert no_trumps.game_level == 3


def test_denomination_repr():
    """Ensure that the denomination repr is correct."""
    assert repr(spades) == 'Denomination("S")'
    assert repr(hearts) == 'Denomination("H")'
    assert repr(diamonds) == 'Denomination("D")'
    assert repr(clubs) == 'Denomination("C")'
    assert repr(no_trumps) == 'Denomination("NT")'


def test_denomination_str():
    """Ensure that the denomination str is correct."""
    assert str(spades) == 'Denomination("S")'
    assert str(hearts) == 'Denomination("H")'
    assert str(diamonds) == 'Denomination("D")'
    assert str(clubs) == 'Denomination("C")'
    assert str(no_trumps) == 'Denomination("NT")'


def test_denomination_full_name():
    """Ensure that the denomination full name is correct."""
    assert spades.full_name == 'spades'
    assert hearts.full_name == 'hearts'
    assert diamonds.full_name == 'diamonds'
    assert clubs.full_name == 'clubs'
    assert no_trumps.full_name == 'no trumps'


def test_denomination_rank():
    """Ensure that the denomination rank is correct."""
    assert spades.rank == 3
    assert hearts.rank == 2
    assert diamonds.rank == 1
    assert clubs.rank == 0
    assert no_trumps.rank == 4


def test_denomination_is_major():
    """Ensure that the denomination is_major is correct."""
    assert spades.is_major
    assert hearts.is_major
    assert not diamonds.is_major
    assert not clubs.is_major
    assert not no_trumps.is_major


def test_denomination_is_minor():
    """Ensure that the denomination is_minor is correct."""
    assert not spades.is_minor
    assert not hearts.is_minor
    assert diamonds.is_minor
    assert clubs.is_minor
    assert not no_trumps.is_minor


def test_denomination_equality():
    """Ensure that the denomination equality is correct."""
    assert spades == Spades()
    assert not clubs == Spades()


def test_denomination_inequality():
    """Ensure that the denomination inequality is correct."""
    assert not spades != Spades()
    assert clubs != Spades()


def test_denomination_greater_than():
    """Ensure that the denomination greater_than is correct."""
    assert not spades > Spades()
    assert not clubs > Spades()
    assert hearts > Clubs()


def test_denomination_greater_than_or_equal():
    """Ensure that the denomination greater_than_or_equal is correct."""
    assert spades >= Spades()
    assert not clubs >= Spades()
    assert hearts >= Clubs()


def test_denomination_less_than():
    """Ensure that the denomination less_than is correct."""
    assert not spades < Spades()
    assert clubs < Spades()
    assert not hearts < Clubs()


def test_denomination_less_than_or_equal():
    """Ensure that the denomination less_than_or_equal is correct."""
    assert spades <= Spades()
    assert clubs <= Spades()
    assert not hearts <= Clubs()
