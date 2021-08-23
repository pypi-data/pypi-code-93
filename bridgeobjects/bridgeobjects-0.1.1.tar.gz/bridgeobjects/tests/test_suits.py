"""A set of tests for the bridgeobjects Suit class."""
import pytest

from ..source.suit import Suit, Spades, Hearts, Diamonds, Clubs  # NoTrumps

spades = Spades()
hearts = Hearts()
diamonds = Diamonds()
clubs = Clubs()
# no_trumps = NoTrumps()


def test_init():
    """Test that the init validation is correct."""
    with pytest.raises(TypeError) as exec_info:
        suit = Suit(['S'])
    with pytest.raises(ValueError) as exec_info:
        suit = Suit('B')


def test_hash():
    """Test that the hash function is correct."""
    suit = Suit('D')
    assert hash(suit) == hash(('D', 'D'))


def test_repr():
    """Test that the repr is returned correctly."""
    assert repr(spades) == 'Suit("S")'


def test_suit_name():
    """Ensure that the suit name is correct."""
    assert spades.name == 'S'
    assert hearts.name == 'H'
    assert diamonds.name == 'D'
    assert clubs.name == 'C'
    # assert no_trumps.name == 'NT'
    assert Suit('').name == ''


def test_suit_str():
    """Ensure that the suit str is correct."""
    assert str(spades) == 'Suit("S")'
    assert str(hearts) == 'Suit("H")'
    assert str(diamonds) == 'Suit("D")'
    assert str(clubs) == 'Suit("C")'
    # assert repr(no_trumps) == 'Suit("NT")'


def test_suit_repr():
    """Ensure that the suit repr is correct."""
    assert repr(spades) == 'Suit("S")'
    assert repr(hearts) == 'Suit("H")'
    assert repr(diamonds) == 'Suit("D")'
    assert repr(clubs) == 'Suit("C")'
    # assert repr(no_trumps) == 'Suit("NT")'


def test_suit_full_name():
    """Ensure that the suit full name is correct."""
    assert spades.full_name == 'spades'
    assert hearts.full_name == 'hearts'
    assert diamonds.full_name == 'diamonds'
    assert clubs.full_name == 'clubs'
    # assert no_trumps.full_name == 'no trumps'


def test_suit_rank():
    """Ensure that the suit rank is correct."""
    assert spades.rank == 3
    assert hearts.rank == 2
    assert diamonds.rank == 1
    assert clubs.rank == 0
    # assert no_trumps.rank == 4


def test_suit_is_major():
    """Ensure that the suit is_major is correct."""
    assert spades.is_major
    assert hearts.is_major
    assert not diamonds.is_major
    assert not clubs.is_major
    # assert not no_trumps.is_major


def test_suit_is_minor():
    """Ensure that the suit is_minor is correct."""
    assert not spades.is_minor
    assert not hearts.is_minor
    assert diamonds.is_minor
    assert clubs.is_minor
    # assert not no_trumps.is_minor


def test_suit_equality():
    """Ensure that the suit equality is correct."""
    assert spades == Spades()
    assert not clubs == Spades()
    assert not clubs == 'C'


def test_suit_inequality():
    """Ensure that the suit inequality is correct."""
    assert not spades != Spades()
    assert clubs != Spades()


def test_suit_greater_than():
    """Ensure that the suit greater_than is correct."""
    assert not spades > Spades()
    assert not clubs > Spades()
    assert hearts > Clubs()


def test_suit_greater_than_or_equal():
    """Ensure that the suit greater_than_or_equal is correct."""
    assert spades >= Spades()
    assert not clubs >= Spades()
    assert hearts >= Clubs()


def test_suit_less_than():
    """Ensure that the suit less_than is correct."""
    assert not spades < Spades()
    assert clubs < Spades()
    assert not hearts < Clubs()


def test_suit_less_than_or_equal():
    """Ensure that the suit less_than_or_equal is correct."""
    assert spades <= Spades()
    assert clubs <= Spades()
    assert not hearts <= Clubs()
