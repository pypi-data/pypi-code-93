"""A set of tests for the bridgeobjects Trick class."""
import pytest

from ..source.trick import Trick
from ..source.card import Card
from ..source.constants import SUITS


def test_trick_repr():
    """Ensure the repr is correct."""
    trick = Trick([Card('AH'), Card('2H'), Card('3H'), Card('4H')])
    assert repr(trick) == 'Trick(cards="AH", "2H", "3H", "4H")'


def test_trick_str():
    """Ensure the str is correct."""
    trick = Trick([Card('AH'), Card('2H'), Card('3H'), Card('4H')])
    assert str(trick) == ('Trick: Leader: '', winner: '', , cards: AH, 2H, 3H, 4H')


def test_trick_cards_setter():
    """Ensure the card setter is correct."""
    trick = Trick(['AH', '2H', '3H', '4H'])
    assert repr(trick) == 'Trick(cards="AH", "2H", "3H", "4H")'

    with pytest.raises(TypeError):
        trick = Trick('AH')

    with pytest.raises(TypeError):
        trick = Trick([1, 2, 3, 4])

    with pytest.raises(ValueError):
        trick = Trick(['GH', '2H', '3H', '4H'])

    # with pytest.raises(ValueError):
    #     trick = Trick(5, ['AH', '2H', '3H', '4H', '5H'])


def test_trick_leader_setter():
    """Ensure the trick leader setter is correct."""
    trick = Trick(['2H', 'AH', '3H', '4H'])
    with pytest.raises(TypeError):
        trick.leader = 1
    with pytest.raises(ValueError):
        trick.leader = 'H'


def test_trick_complete():
    """Ensure the trick complete is correct."""
    trick = Trick(['AH', '2H', '3H', '4H', '5H'])
    with pytest.raises(ValueError):
        trick.complete(SUITS['S'])
    trick = Trick(['2H', 'AH', '3H', '4C'])
    trick.leader = 'E'
    trick.complete(SUITS['S'])
    assert trick.winner == 'S'

    trick = Trick(['2H', 'AH', '3H', '4C'])
    trick.leader = 'E'
    trick.complete()
    assert trick.winner == 'S'

