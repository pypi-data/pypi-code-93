"""A set of tests for the bridgeobjects Card class."""
import pytest

from ..source.card import Card
from ..source.suit import Spades, Hearts, Diamonds, Clubs

ace_of_spades = Card('AS')
queen_of_hearts = Card('QH')
ten_of_clubs = Card('TC')
nine_of_hearts = Card('9H')
ten_of_diamonds = Card('10D')
seven_of_spades = Card('7S')
rag_of_spades = Card('xS')


def test_card_name_valid():
    """Ensure that the card name is correct: valid names."""
    assert ace_of_spades.name == 'AS'
    assert ten_of_clubs.name == 'TC'
    assert nine_of_hearts.name == '9H'
    assert ten_of_diamonds.name == 'TD'
    assert seven_of_spades.name == '7S'
    assert rag_of_spades.name == 'xS'


def test_card_repr_valid():
    """Ensure that the card repr is correct: valid names."""
    assert repr(ace_of_spades) == 'Card("AS")'
    assert repr(ten_of_clubs) == 'Card("TC")'
    assert repr(nine_of_hearts) == 'Card("9H")'
    assert repr(ten_of_diamonds) == 'Card("TD")'
    assert repr(seven_of_spades) == 'Card("7S")'
    assert repr(rag_of_spades) == 'Card("xS")'


def test_card_str_valid():
    """Ensure that the card str is correct: valid names."""
    assert str(ace_of_spades) == 'Card("AS")'
    assert str(ten_of_clubs) == 'Card("TC")'
    assert str(nine_of_hearts) == 'Card("9H")'
    assert str(ten_of_diamonds) == 'Card("TD")'
    assert str(seven_of_spades) == 'Card("7S")'
    assert str(rag_of_spades) == 'Card("xS")'


def test_card_hcp():
    """Ensure that the card hcp is correct."""
    assert ace_of_spades.high_card_points == 4
    assert queen_of_hearts.high_card_points == 2
    assert ten_of_clubs.high_card_points == 0
    assert nine_of_hearts.high_card_points == 0
    assert ten_of_diamonds.high_card_points == 0
    assert seven_of_spades.high_card_points == 0
    assert rag_of_spades.high_card_points == 0


def test_card_name_invalid_rank():
    """Ensure that the card name is correct: invalid rank."""
    with pytest.raises(ValueError):
        card = Card('DS')


def test_card_name_invalid_suit():
    """Ensure that the card name is correct: invalid suit."""
    with pytest.raises(ValueError):
        card = Card('AG')


def test_card_name_invalid():
    """Ensure that the card name is correct: invalid suit and rank."""
    with pytest.raises(ValueError):
        card = Card('DG')


def test_card_name_invalid_length():
    """Ensure that the card name is correct: invalid rank."""
    with pytest.raises(ValueError):
        card = Card('ASQ')


def test_card_rank():
    """Ensure that the card rank is correct."""
    assert ace_of_spades.rank == 'A'
    assert ten_of_clubs.rank == 'T'
    assert nine_of_hearts.rank == '9'
    assert ten_of_diamonds.rank == 'T'
    assert seven_of_spades.rank == '7'
    assert rag_of_spades.rank == 'x'


# def test_card_rank_invalid_rank():
# """Ensure that the card rank is correct: invalid rank."""
# assert Card('DS').rank is None

def test_card_suit_name():
    """Ensure that the card suit_name is correct."""
    assert ace_of_spades.suit_name == 'S'
    assert ten_of_clubs.suit_name == 'C'
    assert nine_of_hearts.suit_name == 'H'
    assert ten_of_diamonds.suit_name == 'D'
    assert seven_of_spades.suit_name == 'S'
    assert rag_of_spades.suit_name == 'S'


def test_card_suit():
    """Ensure that the card suit is correct."""
    assert ace_of_spades.suit.name == Spades().name
    assert ten_of_clubs.suit.name == Clubs().name
    assert nine_of_hearts.suit.name == Hearts().name
    assert ten_of_diamonds.suit.name == Diamonds().name
    assert seven_of_spades.suit.name == Spades().name


def test_card_suit_name_invalid_suit():
    """Ensure that the card suit name is correct: invalid suit."""
    with pytest.raises(ValueError) as e_info:
        assert Card('AX').suit is None


def test_card_value_valid():
    """Ensure that the card value is correct: valid."""
    assert ace_of_spades.value == 13
    assert ten_of_clubs.value == 9
    assert nine_of_hearts.value == 8
    assert ten_of_diamonds.value == 9
    assert seven_of_spades.value == 6
    assert rag_of_spades.value == 0


# def test_card_value_invalid():
# """Ensure that the card value is correct: valid."""
# assert Card('AX').value is None

def test_card_equality():
    """Ensure that the card equality is correct."""
    assert ace_of_spades == Card('AS')
    assert ten_of_clubs == Card('TC')
    assert not nine_of_hearts == Card('AC')
    assert not ten_of_diamonds == Card('JD')
    assert seven_of_spades == Card('7S')


def test_card_inequality():
    """Ensure that the card inequality is correct."""
    assert not ace_of_spades != Card('AS')
    assert not ten_of_clubs != Card('TC')
    assert nine_of_hearts != Card('AC')
    assert ten_of_diamonds != Card('JD')
    assert not seven_of_spades != Card('7S')


def test_card_greater_than():
    """Ensure that the card greater_than is correct."""
    assert not ace_of_spades > Card('AS')
    assert ten_of_clubs > Card('2C')
    assert nine_of_hearts > Card('AC')
    assert not ten_of_diamonds > Card('JD')
    assert not seven_of_spades > Card('7S')


def test_card_greater_than_or_equal():
    """Ensure that the card greater_than_or_equal is correct."""
    assert ace_of_spades >= Card('AS')
    assert ten_of_clubs >= Card('2C')
    assert nine_of_hearts >= Card('AC')
    assert not ten_of_diamonds >= Card('JD')
    assert seven_of_spades >= Card('7S')


def test_card_less_than():
    """Ensure that the card less_than is correct."""
    assert not ace_of_spades < Card('AS')
    assert not ten_of_clubs < Card('2C')
    assert not nine_of_hearts < Card('AC')
    assert ten_of_diamonds < Card('JD')
    assert not seven_of_spades < Card('7S')


def test_card_less_than_or_equal():
    """Ensure that the card less_than_or_equal is correct."""
    assert ace_of_spades <= Card('AS')
    assert not ten_of_clubs <= Card('2C')
    assert not nine_of_hearts <= Card('AC')
    assert ten_of_diamonds <= Card('JD')
    assert seven_of_spades <= Card('7S')
