"""A set of tests for the bridgeobjects Hand class."""
import pytest

from ..source.card import Card
from ..source.hand import Hand
from ..source.suit import Suit, Spades, Hearts, Diamonds, Clubs

spade_suit = Spades()
heart_suit = Hearts()
diamond_suit = Diamonds()
club_suit = Clubs()

hand_list_6332 = ['JS', '8S', '5S', '4S', '3S', '2S',
                  'JH', '8H', '6H',
                  'AD', 'JD',
                  'KC', 'JC']

hand_list_4513 = ['KS', 'TS', '7S', '5S',
                  'KH', 'QH', 'JH', '5H', '2H',
                  'AD',
                  'KC', 'QC', '4C']

hand_list_3343 = ['JS', '8S', '5S',
                   '4H', '3H', '2H',
                   'AD', 'QD', 'JD', '8D',
                   'KC', 'JC', '6C']

hand_list_2443 = ['JS', '8S',
                  '5H', '4H', '3H', '2H',
                  'AD', 'QD', 'JD', '8D',
                  'KC', 'JC', '6C']

hand_list_2443A = ['JS', '8S',
                   'KH', 'QH', 'JH', '2H',
                   'QD', 'JD', 'TD', '8D',
                   'KC', 'JC', 'TC']

hand_list_5512 = ['KS', 'TS', '7S', '5S', '4S',
                  'KH', 'QH', 'JH', '5H', '2H',
                  'AD',
                  'KC', 'QC']

hand_list_6511 = ['JS', '8S', '5S', '4S', '3S', '2S',
                  'JH', '8H', '6H', '3H', '2H',
                  'AD',
                  'JC']

hand_list_6601 = ['JS', '8S', '5S', '4S', '3S', '2S',
                  'AH', 'JH', '8H', '6H', '3H', '2H',
                  'JC']

hand_list_5611 = ['JS', '8S', '6S', '3S', '2S',
                  'QH', 'TH', '9H', '4H', '3H', '2H',
                  'AD',
                  'JC']

hand_pbn_one = '.63.AKQJ87.A9732'

hand_pbn_two = 'A8654.KQ5.T.QJT6'

hand_pbn_three = 'T.QT86.AQ98654.5'

hand_pbn_four = 'A8654.KQ.T.QJT64'

hand_pbn_five = 'A865.JT63.T.QJT6'

short_hand_list = ['KS', 'TS', '7S', '5S', 'KH', '8H', '7H', '5H', '2H',
                   '3D', 'QC', '4C']

long_hand_list = ['KS', 'TS', '7S', '5S', 'KH', '8H', '7H', '5H', '2H',
                  '3D', 'KC', 'QC', '4C', '2C']

short_hand_pbn = '.63.AQ987.A9732'

long_hand_pbn = 'A8654.KQ53.T.QJT6'

hand_list_duplicates = ['KS', 'TS', '7S', '7S', 'KH', '8H', '7H', '5H', '2H',
                        '3D', 'KC', 'KC', '4C']

hand_pbn_duplicates = 'A8654.KK53.T.QQT6'


def test_hand_repr():
    """Ensure that the hand repr is correct."""
    assert repr(Hand(hand_list_6332)) == 'Hand("J85432.J86.AJ.KJ")'
    assert repr(Hand(hand_pbn_one)) == 'Hand(".63.AKQJ87.A9732")'


def test_hand_str():
    """Ensure that the hand str is correct."""
    assert str(Hand(hand_list_6332)) == 'Hand(JS, 8S, 5S, 4S, 3S, 2S, JH, 8H, 6H, AD, JD, KC, JC)'
    assert str(Hand(hand_pbn_one)) == 'Hand(6H, 3H, AD, KD, QD, JD, 8D, 7D, AC, 9C, 7C, 3C, 2C)'


def test_hand_eq():
    """Ensure that the hand equality is correct."""
    assert Hand(hand_list_6332) == Hand("J85432.J86.AJ.KJ")
    assert Hand(hand_pbn_one) != 'Hand(".63.AKQJ82.A9732")'


def test_hand_from_list_card_in_list():
    """Ensure that a hand created from a list of cards is correct: card in list."""
    names = [card.name for card in Hand(hand_list_6332).cards]
    assert Card('4S').name in names
    assert Card('KC').name in names


def test_hand_from_list_card_not_in_list():
    """Ensure that a hand created from a list of cards is correct: card not in list."""
    names = [card.name for card in Hand(hand_list_6332).cards]
    assert not Card('AC').name in names
    assert not Card('2C').name in names


def test_hand_from_pbn_card_in_list():
    """Ensure that a hand created from a pbn string is correct: card in list."""
    names = [card.name for card in Hand(hand_pbn_one).cards]
    assert Card('6H').name in names
    assert Card('AC').name in names


def test_hand_from_pbn_card_not_in_list():
    """Ensure that a hand created from a pbn string is correct: card  not in list."""
    names = [card.name for card in Hand(hand_pbn_one).cards]
    assert not Card('6S').name in names
    assert not Card('4D').name in names


def test_hand_from_pbn_too_many_suits():
    """Ensure that a hand created from a pbn string is correct: card  not in list."""
    with pytest.raises(ValueError):
        assert Hand('A8654.KQ5.T.QJ.T6')


def test_hand_from_pbn_invalid_rank():
    """Ensure that a hand created from a pbn string is correct: card  not in list."""
    with pytest.raises(ValueError):
        assert Hand('A8654.KQ5.0.QJT6')


def test_hand_is_valid_str_list_invalid_item():
    """Ensure that a hand is_valid flag is correct for number of cards: from list."""
    hand_list = [card for card in hand_list_6332]
    hand_list[4] = Card('4S')
    with pytest.raises(TypeError) as exec_info:
        assert Hand(hand_list)


def test_hand_is_valid_card_list_invalid_item():
    """Ensure that a hand is_valid flag is correct for number of cards: from list."""
    hand_list = [Card(card) for card in hand_list_6332]
    hand_list[4] = '4S'
    with pytest.raises(TypeError) as exec_info:
        assert Hand(hand_list)


def test_hand_is_valid_list_invalid_name():
    """Ensure that a hand is_valid flag is correct for number of cards: from list."""
    hand_list = [card for card in hand_list_6332]
    hand_list[4] = '0S'
    with pytest.raises(ValueError) as exec_info:
        assert Hand(hand_list)


def test_hand_is_valid_list():
    """Ensure that a hand is_valid flag is correct for number of cards: from list."""
    assert Hand(hand_list_6332).is_valid
    assert Hand(hand_list_4513).is_valid


def test_hand_is_valid_pbn():
    """Ensure that a hand is_valid flag is correct for number of cards: from pbn."""
    assert Hand(hand_pbn_one).is_valid
    assert Hand(hand_pbn_two).is_valid


def test_hand_is_valid_incorrect_number_of_cards_list():
    """Ensure that a hand is_valid flag is correct for incorrect number of cards: list."""
    assert not Hand(short_hand_list).is_valid
    assert not Hand(long_hand_list).is_valid


def test_hand_is_valid_incorrect_number_of_cards_pbn():
    """Ensure that a hand is_valid flag is correct for incorrect number of cards: pbn."""
    assert not Hand(short_hand_pbn).is_valid
    assert not Hand(long_hand_pbn).is_valid


def test_hand_is_valid_no_parameter():
    """Ensure that a hand is_valid flag is correct: no parameter."""
    assert not Hand().is_valid


def test_hand_is_valid_empty_list():
    """Ensure that a hand is_valid flag is correct: no empty list."""
    assert not Hand([]).is_valid
    assert not Hand().is_valid


def test_hand_is_valid_empty_string():
    """Ensure that a hand is_valid flag is correct: no empty string."""
    assert not Hand('').is_valid


def test_hand_is_valid_duplicate_cards_list():
    """Ensure that a hand is_valid flag is correct for duplicate cards: list."""
    assert not Hand(hand_list_duplicates).is_valid


def test_hand_is_valid_duplicate_cards_pbn():
    """Ensure that a hand is_valid flag is correct for duplicate cards: pbn."""
    assert not Hand(hand_pbn_duplicates).is_valid


def test_hand_suit_cards_list_spades():
    """Ensure that the number of cards in each suit is correct: list spades."""
    assert Hand(hand_list_6332).spades == 6
    assert Hand(hand_list_4513).spades == 4
    assert Hand(long_hand_list).spades == 4


def test_hand_suit_cards_list_hearts():
    """Ensure that the number of cards in each suit is correct: list hearts."""
    assert Hand(hand_list_6332).hearts == 3
    assert Hand(hand_list_4513).hearts == 5
    assert Hand(hand_pbn_one).hearts == 2
    assert Hand(hand_pbn_two).hearts == 3
    assert Hand(long_hand_list).hearts == 5
    assert Hand(short_hand_pbn).hearts == 2


def test_hand_suit_cards_list_diamonds():
    """Ensure that the number of cards in each suit is correct: list diamonds."""
    assert Hand(hand_list_6332).diamonds == 2
    assert Hand(hand_list_4513).diamonds == 1
    assert Hand(hand_pbn_one).diamonds == 6
    assert Hand(hand_pbn_two).diamonds == 1
    assert Hand(long_hand_list).diamonds == 1
    assert Hand(short_hand_pbn).diamonds == 5


def test_hand_suit_cards_list_clubs():
    """Ensure that the number of cards in each suit is correct: list clubs."""
    assert Hand(hand_list_6332).clubs == 2
    assert Hand(hand_list_4513).clubs == 3
    assert Hand(hand_pbn_one).clubs == 5
    assert Hand(hand_pbn_two).clubs == 4
    assert Hand(long_hand_list).clubs == 4
    assert Hand(short_hand_pbn).clubs == 5


def test_hand_suit_holding():
    """Ensure that the suit holding is correct."""
    assert Hand(hand_list_6332).suit_holding['S'] == 6
    assert Hand(hand_list_6332).suit_holding['H'] == 3
    assert Hand(hand_list_6332).suit_holding['D'] == 2
    assert Hand(hand_list_6332).suit_holding['C'] == 2
    assert Hand(hand_list_6332).suit_holding[Spades()] == 6
    assert Hand(hand_list_6332).suit_holding[Suit('H')] == 3
    assert Hand(hand_list_6332).suit_holding[Diamonds()] == 2
    assert Hand(hand_list_6332).suit_holding[Suit('C')] == 2


def test_hand_suit_cards_pbn_spades():
    """Ensure that the number of cards in each suit is correct: pbn spades."""
    assert Hand(hand_pbn_one).spades == 0
    assert Hand(hand_pbn_two).spades == 5
    assert Hand(short_hand_pbn).spades == 0


def test_hand_suit_cards_pbn_hearts():
    """Ensure that the number of cards in each suit is correct: pbn hearts."""
    assert Hand(hand_pbn_one).hearts == 2
    assert Hand(hand_pbn_two).hearts == 3
    assert Hand(short_hand_pbn).hearts == 2


def test_hand_suit_cards_pbn_diamonds():
    """Ensure that the number of cards in each suit is correct: pbn diamonds."""
    assert Hand(hand_pbn_one).diamonds == 6
    assert Hand(hand_pbn_two).diamonds == 1
    assert Hand(short_hand_pbn).diamonds == 5


def test_hand_suit_cards_pbn_clubs():
    """Ensure that the number of cards in each suit is correct: pbn clubs."""
    assert Hand(hand_pbn_one).clubs == 5
    assert Hand(hand_pbn_two).clubs == 4
    assert Hand(short_hand_pbn).clubs == 5


def test_hand_shape_list_valid():
    """Ensure that a hand shape is correct: valid list."""
    assert Hand(hand_list_6332).shape == [6, 3, 2, 2]
    assert Hand(hand_list_4513).shape == [5, 4, 3, 1]


def test_hand_shape_pbn_valid():
    """Ensure that a hand shape is correct: valid pbn."""
    assert Hand(hand_pbn_one).shape == [6, 5, 2, 0]
    assert Hand(hand_pbn_two).shape == [5, 4, 3, 1]


def test_hand_shape_list_invalid():
    """Ensure that a hand shape is correct: invalid list."""
    assert Hand(long_hand_list).shape == [5, 4, 4, 1]


def test_hand_shape_pbn_invalid():
    """Ensure that a hand shape is correct: invalid pbn."""
    assert Hand(short_hand_pbn).shape == [5, 5, 2, 0]


def test_hand_honour_counts_list_aces():
    """Ensure that a hand honour count is correct: list Aces."""
    assert Hand(hand_list_6332).aces == 1
    assert Hand(hand_list_4513).aces == 1


def test_hand_honour_counts_list_kings():
    """Ensure that a hand honour count is correct: list Kings."""
    assert Hand(hand_list_6332).kings == 1
    assert Hand(hand_list_4513).kings == 3


def test_hand_honour_counts_list_queens():
    """Ensure that a hand honour count is correct: list Queens."""
    assert Hand(hand_list_6332).queens == 0
    assert Hand(hand_list_4513).queens == 2


def test_hand_honour_counts_list_jacks():
    """Ensure that a hand honour count is correct: list Jacks."""
    assert Hand(hand_list_6332).jacks == 4
    assert Hand(hand_list_4513).jacks == 1


def test_hand_honour_counts_list_tens():
    """Ensure that a hand honour count is correct: list Tens."""
    assert Hand(hand_list_6332).tens == 0
    assert Hand(hand_list_4513).tens == 1


def test_hand_honour_counts_list_nines():
    """Ensure that a hand honour count is correct: list nines."""
    assert Hand(hand_list_6332).nines == 0
    assert Hand(hand_list_4513).nines == 0


def test_hand_honour_counts_list_tens_and_nines():
    """Ensure that a hand honour count is correct: list tens and nines."""
    assert Hand(hand_list_6332).tens_and_nines == 0
    assert Hand(hand_pbn_three).tens_and_nines == 3


def test_hand_honour_counts_pbn_aces():
    """Ensure that a hand honour count is correct: pbn Aces."""
    assert Hand(hand_pbn_one).aces == 2
    assert Hand(hand_pbn_two).aces == 1


def test_hand_honour_counts_pbn_kings():
    """Ensure that a hand honour count is correct: pbn Kings."""
    assert Hand(hand_pbn_one).kings == 1
    assert Hand(hand_pbn_two).kings == 1


def test_hand_honour_counts_pbn_queens():
    """Ensure that a hand honour count is correct: pbn Queens."""
    assert Hand(hand_pbn_one).queens == 1
    assert Hand(hand_pbn_two).queens == 2


def test_hand_honour_counts_pbn_jacks():
    """Ensure that a hand honour count is correct: pbn Jacks."""
    assert Hand(hand_pbn_one).jacks == 1
    assert Hand(hand_pbn_two).jacks == 1


def test_hand_honour_counts_pbn_tens():
    """Ensure that a hand honour count is correct: pbn Tens."""
    assert Hand(hand_pbn_one).tens == 0
    assert Hand(hand_pbn_two).tens == 2


def test_hand_honour_counts_pbn_nines():
    """Ensure that a hand honour count is correct: pbn Nines."""
    assert Hand(hand_pbn_one).nines == 1
    assert Hand(hand_pbn_two).nines == 0


def test_hand_seven_card_suit_or_better():
    """Ensure that the suit length or better flags are correct: 7 card suit."""
    assert not Hand(hand_list_6332).seven_card_suit_or_better
    assert not Hand(hand_list_4513).seven_card_suit_or_better
    assert not Hand(hand_pbn_one).seven_card_suit_or_better
    assert not Hand(hand_pbn_two).seven_card_suit_or_better
    assert Hand(hand_pbn_three).seven_card_suit_or_better
    assert not Hand(hand_list_3343).seven_card_suit_or_better


def test_hand_six_card_suit_or_better():
    """Ensure that the suit length or better flags are correct: 6 card suit."""
    assert Hand(hand_list_6332).six_card_suit_or_better
    assert not Hand(hand_list_4513).six_card_suit_or_better
    assert Hand(hand_pbn_one).six_card_suit_or_better
    assert not Hand(hand_pbn_two).six_card_suit_or_better
    assert Hand(hand_pbn_three).six_card_suit_or_better
    assert not Hand(hand_list_3343).six_card_suit_or_better


def test_hand_five_card_suit_or_better():
    """Ensure that the suit length or better flags are correct: 5 card suit."""
    assert Hand(hand_list_6332).five_card_suit_or_better
    assert Hand(hand_list_4513).five_card_suit_or_better
    assert Hand(hand_pbn_one).five_card_suit_or_better
    assert Hand(hand_pbn_two).five_card_suit_or_better
    assert Hand(hand_pbn_three).five_card_suit_or_better
    assert not Hand(hand_list_3343).five_card_suit_or_better


def test_hand_seven_card_suit():
    """Ensure that the suit length flags are correct: 7 card suit."""
    assert not Hand(hand_list_6332).seven_card_suit
    assert not Hand(hand_list_4513).seven_card_suit
    assert not Hand(hand_pbn_one).seven_card_suit
    assert not Hand(hand_pbn_two).seven_card_suit
    assert Hand(hand_pbn_three).seven_card_suit


def test_hand_six_card_suit():
    """Ensure that the suit length flags are correct: 6 card suit."""
    assert Hand(hand_list_6332).six_card_suit
    assert not Hand(hand_list_4513).six_card_suit
    assert Hand(hand_pbn_one).six_card_suit
    assert not Hand(hand_pbn_two).six_card_suit
    assert not Hand(hand_pbn_three).six_card_suit


def test_hand_five_card_suit():
    """Ensure that the suit length flags are correct: 5 card suit."""
    assert not Hand(hand_list_6332).five_card_suit
    assert Hand(hand_list_4513).five_card_suit
    assert Hand(hand_pbn_one).five_card_suit
    assert Hand(hand_pbn_two).five_card_suit
    assert not Hand(hand_pbn_three).five_card_suit


def test_hand_five_card_major_or_better():
    """Ensure that the long major or better flags are correct: 5 cards."""
    assert Hand(hand_list_6332).five_card_major_or_better
    assert Hand(hand_list_4513).five_card_major_or_better
    assert not Hand(hand_list_3343).five_card_major_or_better


def test_hand_five_card_major_suit():
    """Ensure that the 5 card major is correct."""
    assert Hand(hand_list_6332).five_card_major_suit == spade_suit
    assert Hand(hand_list_4513).five_card_major_suit == heart_suit
    assert Hand(hand_list_3343).five_card_major_suit is None
    assert Hand(hand_list_6601).five_card_major_suit == spade_suit
    assert Hand(hand_list_5611).five_card_major_suit == heart_suit


def test_hand_four_card_major_or_better():
    """Ensure that the long major or better flags are correct: 4 cards."""
    assert Hand(hand_list_6332).four_card_major_or_better
    assert Hand(hand_list_4513).four_card_major_or_better
    assert not Hand(hand_list_3343).four_card_major_or_better


def test_hand_five_four_or_better():
    """Ensure that five/four or better works."""
    assert not Hand(hand_list_6332).five_four_or_better
    assert Hand(hand_list_4513).five_four_or_better


def test_hand_five_five_or_better():
    """Ensure that five/five or better works."""
    assert not Hand(hand_list_6332).five_five_or_better
    assert not Hand(hand_list_4513).five_five_or_better
    assert Hand(hand_list_5512).five_five_or_better


def test_hand_five_four():
    """Ensure that five/four works."""
    assert not Hand(hand_list_6332).five_four
    assert Hand(hand_list_4513).five_four
    assert not Hand(hand_list_5512).five_four


def test_hand_five_five():
    """Ensure that five/five works."""
    assert not Hand(hand_list_6332).five_five
    assert not Hand(hand_list_4513).five_five
    assert Hand(hand_list_5512).five_five


def test_hand_six_four():
    """Ensure that six/four works."""
    assert not Hand(hand_list_6332).six_four
    assert not Hand(hand_list_4513).six_four
    assert Hand(hand_list_6511).six_four


def test_hand_six_sic():
    """Ensure that six/four works."""
    assert not Hand(hand_list_6332).six_six
    assert not Hand(hand_list_6511).six_six
    assert Hand(hand_list_6601).six_six


def test_hand_four_card_major_suit():
    """Ensure that the 4 card major is correct."""
    assert Hand(hand_list_6332).four_card_major_suit == spade_suit
    assert Hand(hand_list_4513).four_card_major_suit == heart_suit
    assert Hand(hand_list_3343).four_card_major_suit is None
    assert Hand(hand_list_2443).four_card_major_suit == heart_suit


def test_hand_five_card_major():
    """Ensure that the long major flags are correct: 5 cards."""
    assert not Hand(hand_list_6332).five_card_major
    assert Hand(hand_list_4513).five_card_major
    assert not Hand(hand_list_3343).five_card_major


def test_hand_four_card_major():
    """Ensure that the long major flags are correct: 4 cards."""
    assert Hand(hand_list_6332).four_card_major
    assert Hand(hand_list_4513).four_card_major
    assert not Hand(hand_list_3343).four_card_major


def test_hand_equal_long_suits():
    """Ensure that the equal_long_suits flag is correct."""
    assert not Hand(hand_list_6332).equal_long_suits
    assert Hand(hand_pbn_four).equal_long_suits


def test__hand_assignment():
    """Ensure that hand assignment checks work."""
    hand = Hand()
    cards = []
    for card in hand_list_4513:
        cards.append(Card(card))
    hand.cards = cards
    pbn_string = 'KT75.KQJ52.A.KQ4'
    assert repr(hand) == f'Hand("{pbn_string}")'


def test__hand_assignment_invalid_type():
    """Ensure that hand assignment checks work."""
    hand = Hand()
    cards = {}
    for card in hand_list_4513:
        cards[card] = Card(card)
    with pytest.raises(TypeError) as exec_info:
        hand.cards = cards


def test_hand_get_longest_suit_five_five():
    """Ensure that get longest suit is correct for five five."""
    hand = Hand(hand_list_5512)
    assert hand.shape == [5, 5, 2, 1]
    assert hand.longest_suit == spade_suit


def test_hand_get_longest_suit_four_four():
    """Ensure that get longest suit is correct for four four."""
    hand = Hand(hand_list_2443)
    assert hand.shape == [4, 4, 3, 2]
    assert hand.longest_suit == diamond_suit


def test_hand_get_longest_suit_after_hand_assignment():
    """Ensure that get longest suit is correct after hand assignment."""
    hand = Hand()
    hand.cards = [Card(card) for card in hand_list_4513]
    assert hand.longest_suit == heart_suit


def test_hand_get_third_longest_suit():
    """Ensure that third longest suit is correct."""
    assert Hand(hand_list_6332).third_suit == diamond_suit
    assert Hand(hand_list_4513).third_suit == club_suit


def test_hand_suits_by_length():
    """Ensure the suits_by_length list is correct."""
    assert Hand(hand_list_6332).suits_by_length[0].name == 'S'
    assert Hand(hand_list_6332).suits_by_length[1].name == 'H'
    assert Hand(hand_list_6332).suits_by_length[2].name == 'D'
    assert Hand(hand_list_6332).suits_by_length[3].name == 'C'

    assert Hand(hand_list_4513).suits_by_length[0].name == 'H'
    assert Hand(hand_list_4513).suits_by_length[1].name == 'S'
    assert Hand(hand_list_4513).suits_by_length[2].name == 'C'
    assert Hand(hand_list_4513).suits_by_length[3].name == 'D'

    assert Hand(hand_list_3343).suits_by_length[0].name == 'D'
    assert Hand(hand_list_3343).suits_by_length[1].name == 'S'
    assert Hand(hand_list_3343).suits_by_length[2].name == 'H'
    assert Hand(hand_list_3343).suits_by_length[3].name == 'C'

    assert Hand(hand_pbn_one).suits_by_length[0].name == 'D'
    assert Hand(hand_pbn_one).suits_by_length[1].name == 'C'
    assert Hand(hand_pbn_one).suits_by_length[2].name == 'H'
    assert Hand(hand_pbn_one).suits_by_length[3].name == 'S'

    assert Hand(hand_pbn_five).suits_by_length[0].name == 'S'
    assert Hand(hand_pbn_five).suits_by_length[1].name == 'H'
    assert Hand(hand_pbn_five).suits_by_length[2].name == 'C'
    assert Hand(hand_pbn_five).suits_by_length[3].name == 'D'


def test_hand_longest_suit():
    """Ensure the longest_suit is correct."""
    assert Hand(hand_list_6332).longest_suit.name == 'S'
    assert Hand(hand_list_4513).longest_suit.name == 'H'
    assert Hand(hand_list_3343).longest_suit.name == 'D'
    assert Hand(hand_list_2443).longest_suit.name == 'D'
    assert Hand(hand_pbn_one).longest_suit.name == 'D'
    assert Hand(hand_pbn_two).longest_suit.name == 'S'
    assert Hand(hand_pbn_three).longest_suit.name == 'D'
    assert Hand(hand_pbn_four).longest_suit.name == 'S'
    assert Hand(hand_pbn_five).longest_suit.name == 'C'
    assert Hand(hand_list_5611).longest_suit.name == 'H'


def test_hand_second_suit():
    """Ensure the second longest_suit is correct."""
    assert Hand(hand_list_6332).second_suit.name == 'H'
    assert Hand(hand_list_4513).second_suit.name == 'S'
    assert Hand(hand_list_3343).second_suit.name == 'S'
    assert Hand(hand_list_2443).second_suit.name == 'H'
    assert Hand(hand_pbn_one).second_suit.name == 'C'
    assert Hand(hand_pbn_two).second_suit.name == 'C'
    assert Hand(hand_pbn_three).second_suit.name == 'H'
    assert Hand(hand_pbn_four).second_suit.name == 'C'
    assert Hand(hand_pbn_five).second_suit.name == 'H'


def test_hand_distribution_points():
    """Ensure the hand's distribution points is correct."""
    assert Hand(hand_list_6332).distribution_points == 2
    assert Hand(hand_list_4513).distribution_points == 2
    assert Hand(hand_list_3343).distribution_points == 0
    assert Hand(hand_list_2443).distribution_points == 1
    assert Hand(hand_pbn_one).distribution_points == 4
    assert Hand(hand_pbn_two).distribution_points == 2
    assert Hand(hand_pbn_three).distribution_points == 4
    assert Hand(hand_pbn_four).distribution_points == 3
    assert Hand(hand_pbn_five).distribution_points == 2


def test_hand_high_card_points():
    """Ensure the hand's high card points is correct."""
    assert Hand(hand_list_6332).high_card_points == 11
    assert Hand(hand_list_4513).high_card_points == 18
    assert Hand(hand_list_3343).high_card_points == 12
    assert Hand(hand_list_2443).high_card_points == 12
    assert Hand(hand_pbn_one).high_card_points == 14
    assert Hand(hand_pbn_two).high_card_points == 12
    assert Hand(hand_pbn_three).high_card_points == 8
    assert Hand(hand_pbn_four).high_card_points == 12
    assert Hand(hand_pbn_five).high_card_points == 8


def test_hand_four_four_four_one():
    """Ensure the hand's four_four_four_one is correct."""
    assert not Hand(hand_list_6332).four_four_four_one
    assert Hand(hand_pbn_five).four_four_four_one


def test_hand_is_balanced():
    """Ensure the hand's is_balanced is correct."""
    assert not Hand(hand_list_6332).is_balanced
    assert Hand(hand_list_3343).is_balanced
    assert Hand(hand_list_2443).is_balanced
    assert not Hand(hand_pbn_two).is_balanced
    assert not Hand(hand_pbn_five).is_balanced


def test_hand_is_semi_balanced():
    """Ensure the hand's is_semi_balanced is correct."""
    assert Hand(hand_list_6332).is_semi_balanced
    assert Hand(hand_list_3343).is_semi_balanced
    assert Hand(hand_list_2443).is_semi_balanced
    assert Hand(hand_pbn_two).is_semi_balanced
    assert not Hand(hand_pbn_five).is_semi_balanced


def test_hand_honours():
    """Ensure the hand's honours is correct."""
    hand = Hand(hand_list_6332)
    assert hand.honours == {'S': 1, 'H':1, 'D':2, 'C': 2}
    hand = Hand(hand_list_5512)
    assert hand.honours == {'S': 2, 'H':3, 'D':1, 'C': 2}


# No longer set at hand level default is True
# def test_hand_high_card_left_default():
#     """Ensure the hand's high_card_left default is correct."""
#     hand = Hand(hand_list_6332)
#     assert hand.high_card_left


def test_hand_rule_of_twenty():
    """Ensure the hand's rule_of_twenty flag is correct."""
    assert Hand(hand_list_6332).rule_of_twenty
    assert Hand(hand_list_4513).rule_of_twenty
    assert not Hand(hand_list_3343).rule_of_twenty
    assert Hand(hand_list_2443).rule_of_twenty
    assert Hand(hand_pbn_one).rule_of_twenty
    assert Hand(hand_pbn_two).rule_of_twenty
    assert not Hand(hand_pbn_three).rule_of_twenty
    assert Hand(hand_pbn_four).rule_of_twenty
    assert not Hand(hand_pbn_five).rule_of_twenty


def test_hand_rule_of_nineteen():
    """Ensure the hand's rule_of_nineteen flag is correct."""
    assert Hand(hand_list_6332).rule_of_nineteen
    assert Hand(hand_list_4513).rule_of_nineteen
    assert Hand(hand_list_3343).rule_of_nineteen
    assert Hand(hand_list_2443).rule_of_nineteen
    assert Hand(hand_pbn_one).rule_of_nineteen
    assert Hand(hand_pbn_two).rule_of_nineteen
    assert Hand(hand_pbn_three).rule_of_nineteen
    assert Hand(hand_pbn_four).rule_of_nineteen
    assert not Hand(hand_pbn_five).rule_of_nineteen


def test_hand_suit_points():
    """Ensure the hand's suit_points is correct."""
    assert Hand(hand_list_6332).suit_points(spade_suit) == 1
    assert Hand(hand_list_6332).suit_points(club_suit) == 4
    assert Hand(hand_pbn_one).suit_points(spade_suit) == 0


def test_hand_rule_of_fourteen():
    """Ensure the hand's rule_of_fourteen flag is correct."""
    assert not Hand(hand_list_6332).rule_of_fourteen(spade_suit)
    assert not Hand(hand_list_6332).rule_of_fourteen(spade_suit)
    assert not Hand(hand_pbn_one).rule_of_fourteen(heart_suit)
    assert Hand(hand_pbn_one).rule_of_fourteen(diamond_suit)


def test_hand_solid_suit_honours():
    """Ensure the hand's solid_suit_honours flag is correct."""
    assert not Hand(hand_list_6332).solid_suit_honours(spade_suit)
    assert Hand(hand_pbn_one).solid_suit_honours(diamond_suit)


def test_maximum_points_for_shape():
    """Ensure that the maximum points for a shape is correct."""
    assert Hand().maximum_points_for_shape([9, 3, 1, 0]) == 23
    assert Hand().maximum_points_for_shape([4, 3, 3, 3]) == 37


def test_honour_sequences():
    """Ensure that the hand honour sequences are correct."""
    sequences = {'S': [], 'H': [Card('KH'), Card('QH'), Card('JH')],
                 'D': [], 'C': []}
    assert Hand(hand_list_4513).honour_sequences() == sequences


def test_touching_honours():
    """Ensure that the touching honours are correct."""
    sequences = {'S': [], 'H': [],
                 'D': [], 'C': [Card('KC'), Card('QC')]}
    assert Hand(hand_list_4513).touching_honours() == sequences


def test_honour_sequences_higher_honour():
    """Ensure that the hand honour sequences with a higher honour are correct."""
    sequences = {'S': [], 'H': [], 'D': [], 'C': []}
    assert Hand(hand_list_3343).honour_sequences() == sequences

    sequences = {'S': [],
                 'H': [Card('KH'), Card('QH'), Card('JH')],
                 'D': [Card('QD'), Card('JD'), Card('TD')],
                 'C': []}
    assert Hand(hand_list_2443A).honour_sequences() == sequences


def test_cards_by_suit():
    """Ensure cards by suit is correct."""
    assert Card('8S') in Hand(hand_list_6332).cards_by_suit['S']
    assert Card('AS') not in Hand(hand_list_6332).cards_by_suit['S']
    assert Card('AD') in Hand(hand_list_6332).cards_by_suit['D']
    assert Card('AD') not in Hand(hand_list_6332).cards_by_suit['S']
    assert Card('QD') not in Hand(hand_list_6332).cards_by_suit['D']


def test_internal_sequences():
    """Ensure that the hand honour sequences with a higher honour are correct."""
    assert Hand(hand_list_3343).internal_sequences() == [Card('QD')]
    assert Hand(hand_list_2443A).internal_sequences() == [Card('JC')]
    assert Hand(hand_list_5611).internal_sequences() == [Card('TH')]


# No longer set at hand level default is True
# def test_hand_high_card_left_setter():
#     """Ensure the hand's high_card_left is correct."""
#     hand = Hand(hand_list_6332)
#     with pytest.raises(TypeError) as exc_info:
#         hand.high_card_left = 1
#     assert True


def test_sorted_cards():
    """Ensure sorted_cards works correctly."""
    # hand_pbn_two = 'A8654.KQ5.T.QJT6'
    hand = Hand(hand_pbn_two)

    assert hand.cards[0] == Card('AS')
    assert hand.cards[-1] == Card('6C')

    cards = hand.sorted_cards()
    assert cards[0] == Card('AS')
    assert cards[-1] == Card('TD')

    cards = hand.sorted_cards('HSDC')
    assert cards[0] == Card('KH')
    assert cards[-1] == Card('6C')

    cards = hand.sorted_cards(high_card_left=False)
    assert cards[0] == Card('4S')
    assert cards[-1] == Card('TD')

    cards = hand.sorted_cards('HSDC', high_card_left=False)
    assert cards[0] == Card('5H')
    assert cards[-1] == Card('QC')

    # hand.high_card_left = False
    cards = hand.sorted_cards('HSDC', False)
    assert cards[0] == Card('5H')
    assert cards[-1] == Card('QC')


def test_sorted_cards_suit_order():
    """Ensure sorted_cards works correctly."""
    # hand_pbn_two = 'A8654.KQ5.T.QJT6'
    hand = Hand(hand_pbn_two)
    assert hand.suit_order == 'SHCD'

    assert hand.cards[0] == Card('AS')
    assert hand.cards[-1] == Card('6C')

    hand.suit_order = 'HSDC'
    cards = hand.sorted_cards()
    assert cards[0] == Card('KH')
    assert cards[3] == Card('AS')
    assert cards[-5] == Card('TD')
    assert cards[-1] == Card('6C')


def test_suit_order_assignment():
    """Ensure suit_orsder assignment works correctly."""
    # hand_pbn_two = 'A8654.KQ5.T.QJT6'
    hand = Hand(hand_pbn_two)
    with pytest.raises(TypeError) as exec_info:
        hand.suit_order = ['S', 'D', 'H', 'C']
    with pytest.raises(ValueError) as exec_info:
        hand.suit_order = 'ADHCB'
    with pytest.raises(ValueError) as exec_info:
        hand.suit_order = 'SHDS'
    with pytest.raises(ValueError) as exec_info:
        hand.suit_order = 'SHDA'


def test_cards_in_suit():
    """Ensure cards in suiy works correctly."""
    hand = Hand(hand_list_6332)
    assert hand.cards_in_suit(spade_suit) == 6
    hand = Hand(hand_list_4513)
    assert hand.cards_in_suit(diamond_suit) == 1
