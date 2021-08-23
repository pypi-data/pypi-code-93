"""A set of tests for the bridgeobjects Board class."""
import pytest
from ..source.board import Board
from ..source.hand import Hand
from ..source.call import Call
from ..source.card import Card
from ..source.auction import Auction
from ..source.contract import Contract


def test_board_instantiate():
    """Ensure that a board is created correctly."""
    board = Board(12)
    assert board.identifier == "12"


def test_board_no_identifier():
    """Ensure that a board is created correctly."""
    board = Board(None)
    assert board.identifier == ""


def test_board_invalid_identifier():
    """Ensure that a board is created correctly."""
    with pytest.raises(TypeError):
        board = Board(['a'])


def test_board_repr():
    """Ensure that a board repr works correctly."""
    hands = [
        Hand('A8765.QT.K9.AT87'),
        Hand('J42.AJ7632.J.632'),
        Hand('QT3.85.Q86.KQJ54'),
        Hand('K9.K94.AT75432.9'),
    ]
    board = Board(12, hands=hands)
    assert repr(board) == ('Board("12", {'
                           '0: Hand("A8765.QT.K9.AT87"), '
                           '1: Hand("J42.AJ7632.J.632"), '
                           '2: Hand("QT3.85.Q86.KQJ54"), '
                           '3: Hand("K9.K94.AT75432.9")})')


def test_board_str():
    """Ensure that a board str works correctly."""
    board = Board(12)
    assert str(board) == 'Board("12")'


def test_board_number_setter_no_identifier():
    """Ensure that a board number setter works correctly: no identifier."""
    board = Board()
    assert board.identifier == ""


def test_board_number_setter_empty_string():
    """Ensure that a board number setter works correctly: empty string."""
    board = Board("")
    assert board.identifier == ""


def test_board_number_setter_integer():
    """Ensure that a board number setter works correctly: integer."""
    board = Board()
    board = Board(11)
    assert board.identifier == "11"


def test_board_number_setter_integer_string():
    """Ensure that a board number setter works correctly: integer string."""
    board = Board()
    board = Board("12")
    assert board.identifier == "12"


def test_board_number_setter_float():
    """Ensure that a board number setter works correctly: float."""
    board = Board()
    with pytest.raises(TypeError):
        board = Board(13.0000)


def test_board_number_setter_float_string():
    """Ensure that a board number setter works correctly: empty string."""
    board = Board()
    with pytest.raises(TypeError):
        board = Board(14.0001)


def test_board_number_setter_string_of_integers():
    """Ensure that a board number setter works correctly: string of integers."""
    board = Board()
    board = Board("fifteen")
    assert board.identifier == "fifteen"


def test_board_number_setter_string():
    """Ensure that a board number setter works correctly: string."""
    board = Board()
    board.identifier = "abc"
    assert board.identifier == "abc"


board = Board()


def test_board_vulnerable_setter_none_default():
    """Ensure that a board vulnerable setter works correctly: no parameter"""
    assert board.vulnerable == ''


def test_board_vulnerable_setter_none():
    """Ensure that a board vulnerable setter works correctly: None (valid)."""
    board.vulnerable = ''
    assert board.vulnerable == ''


def test_board_vulnerable_setter_all():
    """Ensure that a board vulnerable setter works correctly: All (convert to Both)."""
    board.vulnerable = 'All'
    assert board.vulnerable == 'Both'


def test_board_vulnerable_setter_both():
    """Ensure that a board vulnerable setter works correctly: Both."""
    board.vulnerable = 'Both'
    assert board.vulnerable == 'Both'


def test_board_vulnerable_setter_valid_parameter():
    """Ensure that a board vulnerable setter works correctly: EW."""
    board.vulnerable = 'EW'
    assert board.vulnerable == 'EW'


def test_board_vulnerable_setter_invalid_parameter():
    """Ensure that a board vulnerable setter works correctly: WE."""
    with pytest.raises(ValueError):
        board.vulnerable = 'WE'
    with pytest.raises(AssertionError):
        assert board.vulnerable is None


board = Board()


def test_board_declarer_setter_no_parameter():
    """Ensure that a board declarer setter works correctly: no parameter."""
    assert board.declarer == ''
    assert board.declarer_index == -1


def test_board_declarer_setter_valid_parameter():
    """Ensure that a board declarer setter works correctly: N."""
    board.declarer = 'N'
    assert board.declarer == 'N'
    assert board.declarer_index == 0


def test_board_declarer_setter_invalid_parameter():
    """Ensure that a board declarer setter works correctly: invalid parameter."""
    with pytest.raises(AssertionError):
        board.declarer = 'M'
    with pytest.raises(AssertionError):
        assert board.declarer is None
    with pytest.raises(AssertionError):
        assert board.declarer_index == -1


def test_board_declarer_setter_question():
    """Ensure that a board declarer setter works correctly: question point."""
    with pytest.raises(AssertionError):
        board.declarer = "?"
    with pytest.raises(AssertionError):
        assert board.declarer is None
    with pytest.raises(AssertionError):
        assert board.declarer_index == -1


board = Board()


def test_board_declarer_index_setter_no_parameter():
    """Ensure that a board declarer index setter works correctly: no parameter."""
    with pytest.raises(AssertionError):
        assert board.declarer is None
    with pytest.raises(AssertionError):
        assert board.declarer_index == -1


def test_board_declarer_index_setter_valid_parameter():
    """Ensure that a board declarer index setter works correctly: N."""
    board.declarer_index = 1
    assert board.declarer == 'E'
    assert board.declarer_index == 1


def test_board_declarer_index_setter_invalid_parameter():
    """Ensure that a board declarer index setter works correctly: invalid parameter."""
    board.declarer_index = 3
    assert board.declarer == 'W'
    assert board.declarer_index == 3


def test_board_declarer_index_setter_question():
    """Ensure that a board declarer index setter works correctly: question point."""
    board.declarer_index = 4
    assert board.declarer == ''
    assert board.declarer_index == -1


def test_board_dealer_setter_no_parameter():
    """Ensure that a board dealer setter works correctly: no parameter."""
    board = Board()
    assert board.dealer == ''
    assert board.dealer_index == -1


def test_board_dealer_setter_valid_parameter():
    """Ensure that a board dealer setter works correctly: valid parameter."""
    board = Board()
    board.dealer = 'S'
    assert board.dealer == 'S'
    assert board.dealer_index == 2
    board.dealer = 'W'
    assert board.dealer == 'W'
    assert board.dealer_index == 3


def test_board_dealer_setter_invalid_parameter_string():
    """Ensure that a board dealer setter works correctly: invalid parameter."""
    board = Board()
    with pytest.raises(ValueError) as exc_info:
        board.dealer = 'Q'
    assert board.dealer == ''
    assert board.dealer_index == -1


def test_board_dealer_setter_invalid_parameter_integer():
    """Ensure that a board dealer setter works correctly: invalid parameter."""
    board = Board()
    with pytest.raises(ValueError):
        board.dealer_index = 4
    assert board.dealer == ''
    assert board.dealer_index == -1


def test_board_dealer_index_setter_no_parameter():
    """Ensure that a board dealer index setter works correctly: no parameter."""
    board = Board()
    assert board.dealer == ''
    assert board.dealer_index == -1


def test_board_dealer_index_setter_valid_parameter():
    """Ensure that a board dealer index setter works correctly: valid parameter."""
    board.dealer_index = 2
    assert board.dealer == 'S'
    board.dealer_index = 3
    assert board.dealer == 'W'
    assert board.dealer_index == 3


def test_board_dealer_index_setter_invalid_parameter_string():
    """Ensure that a board dealer index setter works correctly: invalid parameter."""
    with pytest.raises(ValueError):
        board.dealer_index = 'Q'
    assert board.dealer == ''
    assert board.dealer_index == -1


# def test_board_dealer_index_setter_invalid_parameter_integer():
# """Ensure that a board dealer index setter works correctly: invalid parameter."""
# board.dealer = -1
# assert board.dealer is None
# assert board.dealer_index == -1


def test_board_contract_setter_no_parameter():
    """Ensure that a board contract setter works correctly: no parameter."""
    assert board.contract.declarer == ""
    assert board.contract.call.name == ""


def test_board_contract_setter_valid_not_doubled():
    """Ensure that a board contract setter works correctly: valid not doubled."""
    board.contract = Contract(name="5D")
    assert board.contract.name == "5D"


# def test_board_contract_setter_valid_doubled():
# """Ensure that a board contract setter works correctly: valid doubled."""
# board.contract = "5DD"
# assert board.contract == "5DD")

# def test_board_contract_setter_valid_redoubled():
# """Ensure that a board contract setter works correctly: valid redoubled."""
# board.contract = "5DR"
# assert board.contract == "5DR")

# def test_board_contract_setter_valid_doubled_X():
# """Ensure that a board contract setter works correctly: valid doubled X."""
# board.contract = "5DX"
# assert board.contract == "5DD")

# def test_board_contract_setter_valid_redoubled_X():
# """Ensure that a board contract setter works correctly: valid redoubled XX."""
# board.contract = "5DXX"
# assert board.contract == "5DR")


def test_board_auction_setter_empty_list():
    """Ensure that a board auction setter works correctly: empty tuple."""
    board = Board()
    board.auction = Auction()
    assert board.auction.calls == []


def test_board_auction_setter_invalid_termination():
    """Ensure that a board auction setter works correctly: no 3 Ps."""
    board = Board()
    board.auction.calls = ['1NT', '2C']
    assert board.auction.calls == [Call('1NT'), Call('2C')]


def test_board_auction_setter_invalid_call():
    """Ensure that a board auction setter works correctly: invalid call."""
    board = Board()
    with pytest.raises(ValueError):
        board.auction.calls = ['1NT', 'P', '2Q', 'P', 'P', 'P']


def test_board_auction_setter_valid_auction():
    """Ensure that a board auction setter works correctly: valid auction."""
    board = Board()
    board.auction = Auction()
    board.auction.calls = ['1NT', 'P', '2NT', 'P', 'P', 'P']
    assert board.auction.calls == [Call('1NT'), Call('P'), Call('2NT'),
                                   Call('P'), Call('P'), Call('P')]


def test_board_invalid_hands():
    """Test invalid hands."""
    with pytest.raises(TypeError):
        hand_list = [
            Hand('A8765.QT.K9.AT87'),
            Hand('J42.AJ7632.J.632'),
            Hand('QT3.85.Q86.KQJ54'),
            Hand('K9.K94.AT75432.9'),
        ]
        hands = tuple(hand_list)
        board = Board(hands=hands)


def test_board_invalid_hand_type_list():
    """Test invalid hands."""
    with pytest.raises(TypeError):
        hand_list = [
            Card('AS'),
            Hand('J42.AJ7632.J.632'),
            Hand('QT3.85.Q86.KQJ54'),
            Hand('K9.K94.AT75432.9'),
        ]
        board = Board(hands=hand_list)


def test_board_invalid_hand_key_int():
    """Test invalid hands."""
    with pytest.raises(ValueError):
        hand_dict= {
            0:Hand('A8765.QT.K9.AT87'),
            1: Hand('J42.AJ7632.J.632'),
            4: Hand('QT3.85.Q86.KQJ54'),
            3: Hand('K9.K94.AT75432.9'),
        }
        board = Board(hands=hand_dict)


def test_board_invalid_hand_key_alpha():
    """Test invalid hands."""
    with pytest.raises(ValueError):
        hand_dict= {
            'N':Hand('A8765.QT.K9.AT87'),
            'E': Hand('J42.AJ7632.J.632'),
            'A': Hand('QT3.85.Q86.KQJ54'),
            'W': Hand('K9.K94.AT75432.9'),
        }
        board = Board(hands=hand_dict)


def test_board_valid_dict():
    """Test invalid hands."""
    hand_dict= {
        'N':Hand('A8765.QT.K9.AT87'),
        'E': Hand('J42.AJ7632.J.632'),
        'S': Hand('QT3.85.Q86.KQJ54'),
        'W': Hand('K9.K94.AT75432.9'),
    }
    board = Board(hands=hand_dict)
    assert board.hands_by_index[0].cards[5].name == 'QH'
    assert board.hands_by_index[1].cards[-4].name == 'JD'
    assert board.hands_by_index[2].cards[2].name == '3S'
    assert board.hands_by_index[3].cards[1].name == '9S'
    assert board.hands_by_index[3].cards[-1].name == '9C'


def test_board_invalid_hand_type_dict_key():
    """Test invalid hands."""
    with pytest.raises(TypeError):
        hand_dict= {
            'N': Card('AS'),
            'E': Hand('J42.AJ7632.J.632'),
            'S': Hand('QT3.85.Q86.KQJ54'),
            'W': Hand('K9.K94.AT75432.9'),
        }
        board = Board(hands=hand_dict)


def test_board_given_three_hands():
    """Ensure that the built fourth hand is correct."""
    hand_list = [
        Hand('A8765.QT.K9.AT87'),
        Hand('J42.AJ7632.J.632'),
        Hand('QT3.85.Q86.KQJ54'),
    ]
    board = Board(hands=hand_list)
    assert len(board.hands) == 8
    assert len(board.hands_by_index) == 4
    assert len(board.hands_by_seat) == 4
    missing_hand = board.hands[3]
    # missing_hand [KS, 9S, KH, 9H, 4H, AD, TD, 7D, 5D, 4D, 3D, 2D, 9C]
    assert Card('9S') in missing_hand.cards
    assert Card('9C') in missing_hand.cards


def test_board_hands_by_index_init():
    """Ensure that hands by index is correct."""
    hands = [
        Hand('A8765.QT.K9.AT87'),
        Hand('J42.AJ7632.J.632'),
        Hand('QT3.85.Q86.KQJ54'),
        Hand('K9.K94.AT75432.9'),
    ]
    board = Board(hands=hands)
    assert board.hands_by_index[0].cards[5].name == 'QH'
    assert board.hands_by_index[1].cards[-4].name == 'JD'
    assert board.hands_by_index[2].cards[2].name == '3S'
    assert board.hands_by_index[3].cards[1].name == '9S'
    assert board.hands_by_index[3].cards[-1].name == '9C'


def test_board_set_hands_by_index():
    """Ensure that hands by index is correct."""
    hands = [
        Hand('A8765.QT.K9.AT87'),
        Hand('J42.AJ7632.J.632'),
        Hand('QT3.85.Q86.KQJ54'),
        Hand('K9.K94.AT75432.9'),
    ]
    board = Board()
    board.hands = hands
    assert board.hands_by_index[0].cards[5].name == 'QH'
    assert board.hands_by_index[1].cards[-4].name == 'JD'
    assert board.hands_by_index[2].cards[2].name == '3S'
    assert board.hands_by_index[3].cards[1].name == '9S'
    assert board.hands_by_index[3].cards[-1].name == '9C'


def test_board_hands_by_seat():
    """Ensure that hands by seat is correct."""
    hands = [
        Hand('A8765.QT.K9.AT87'),
        Hand('J42.AJ7632.J.632'),
        Hand('QT3.85.Q86.KQJ54'),
        Hand('K9.K94.AT75432.9'),
    ]
    board = Board(hands=hands)
    assert board.hands_by_seat['N'].cards[5].name == 'QH'
    assert board.hands_by_seat['E'].cards[-4].name == 'JD'
    assert board.hands_by_seat['S'].cards[2].name == '3S'
    assert board.hands_by_seat['W'].cards[1].name == '9S'
    assert board.hands_by_seat['W'].cards[-1].name == '9C'


def test_board_to_pbn():
    """Ensure that board to pbn is correct."""
    hands = [
        Hand('A8765.QT.K9.AT87'),
        Hand('J42.AJ7632.J.632'),
        Hand('QT3.85.Q86.KQJ54'),
        Hand('K9.K94.AT75432.9'),
    ]
    hand_string = 'K9.K94.AT75432.9 A8765.QT.K9.AT87 J42.AJ7632.J.632 QT3.85.Q86.KQJ54'
    board = Board(3, hands=hands)
    board.description = 'test description'
    board.dealer = 'W'
    board_to_pbn = board.board_to_pbn()
    assert board_to_pbn[0] == '[Board "3"]'
    assert board_to_pbn[1] == '[Dealer "W"]'
    assert board_to_pbn[2] == '[Description "test description"]'
    assert board_to_pbn[3] == f'[Deal "W:{hand_string}"]'


full_pack = board.full_pack()


def test_board_full_pack_has_52_cards():
    """Ensure that the full pack has 52 cards."""
    assert len(full_pack) == 52


def test_board_full_pack_contains_cards():
    """Ensure that the full pack contains only cards."""
    for card in full_pack:
        assert type(card) == Card


def test_board_full_pack_contains_no_duplicates():
    """Ensure that the full pack contains no duplicates."""
    used = []
    for card in full_pack:
        assert card.name not in used
        used.append(card.name)


def test_full_pack_suit_count_valid():
    """Ensure that the full pack has 52 cards."""
    spades = [card for card in full_pack if card.suit.name == "S"]
    hearts = [card for card in full_pack if card.suit.name == "H"]
    diamonds = [card for card in full_pack if card.suit.name == "D"]
    clubs = [card for card in full_pack if card.suit.name == "C"]
    assert len(spades) == 13
    assert len(spades) + len(hearts) + len(diamonds) + len(clubs) == 52


def test_full_pack_no_duplicates():
    """Ensure that every card in full_pack is unique."""
    check_pack = []
    for card in full_pack:
        assert card.name not in check_pack
        check_pack.append(card.name)
    assert len(check_pack) == 52
