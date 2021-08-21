"""Test opening lead cards."""
from bridgeobjects import Hand, Auction, Contract, Call, Suit, Board

from ..source.opening_lead_suit import opening_lead_suit

def _get_board(dealer, hand, bids):
    """Return a board based on parameters."""
    board = Board()
    board.dealer = dealer
    board.auction = Auction(bids, board.dealer)
    board.contract = Contract(auction=board.auction)
    board.hands[board.contract.leader] = hand
    return board

def test_four_card_suit():
    """Test that a 4 card suit is selected against NT contract. Partner not bid."""
    hand = Hand('8642.754.A94.987')
    bids = ['1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '005'

def test_best_four_card_suit():
    """Test that the 4 card long suit is selected against NT contract. Partner not bid."""
    hand = Hand('AJ83.754.AQ94.98')
    bids = ['P', '1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '006'

def test_long_suit():
    """Test that the long suit is selected against NT contract. Partner not bid."""
    hand = Hand('A9832.75.AK94.98')
    bids = ['1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('E', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '003'

def test_best_longest_suit():
    """Test that the best longest suit is selected against NT contract. Partner not bid."""
    hand = Hand('A9832.7.AK954.98')
    bids = ['1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('E', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '009'

def test_klinger_3_B_1_i():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('752.87.AJT94.985')
    bids = ['P', '1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '001'


def test_klinger_3_B_1_ii_a():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('752.87.AJT94.985')
    bids = ['P', '1D', 'P', '1NT', 'P', '3D', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '019'

def test_klinger_3_B_1_ii_b():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('752.87.AJT94.985')
    bids = ['P', 'P', '1H', '1NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '020'

def test_klinger_3_B_2_i():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('QJ982.Q4.JT32.98')
    bids = ['1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '001'

def test_klinger_3_B_2_ii_a():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('QJ982.Q4.JT32.98')
    bids = ['1S', 'P', '2H', 'P', '2NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '019'

def test_klinger_3_B_2_ii_b():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('QJ982.Q4.JT32.98')
    bids = ['1NT', 'P', '2C', 'P', '2H', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '019'

def test_klinger_3_B_3_i():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('632.K9753.QT7.J8')
    bids = ['P','1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '003'

def test_klinger_3_B_3_ii_a():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('632.K9753.QT7.J8')
    bids = ['1NT', 'P', '3H', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '019'

def test_klinger_3_B_3_ii_b():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('632.K9753.QT7.J8')
    bids = ['2NT', 'P', '3S', 'P', '4S', 'P', '4NT', 'P', '5H', 'P', '6NT', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '022'

def test_klinger_3_B_4_i():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('QT982.J83.J732.4')
    bids = ['P','1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '001'

def test_klinger_3_B_4_ii_a():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('QT982.J83.J732.4')
    bids = ['P', '1S', 'P', '2D', 'P', '3D', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '019'

# def test_klinger_3_B_4_ii_a(): # Too esoteric
    # """Klinger exercise. Better Card play p15."""
#     hand = Hand('QT982.J83.J732.4')
#     seat = 'W'
#     dealer = 'W'
#     auction = Auction(['P', '1C', 'P', '1NT', 'P', '2NT', 'P', '3NT', 'P', 'P', 'D', 'P', 'P', 'P'], dealer)
#     suit = opening_lead_suit(hand, seat, dealer, auction)
#     assert suit == Suit('C')
#     assert suit.selection_reason == '019'

def test_klinger_3_B_5_i():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('JT986.7.AQT.7432')
    bids = ['P', '1NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')

def test_klinger_3_B_5_i():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('JT986.7.AQT.7432')
    bids = ['P', '1D', '1H', '2D', 'P', '2H', 'P', '2NT', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '021'

def test_klinger_3_B_5_ii():
    """Klinger exercise. Better Card play p15."""
    hand = Hand('JT986.7.AQT.7432')
    bids = ['P', '3C', 'P', '3NT', 'P', 'P', 'P']
    board = _get_board('W', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '021'

def test_klinger_4_1_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('AJ2.J7.9743.A852')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '014'

def test_klinger_4_1_ii_a():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('AJ2.J7.9743.A852')
    dealer = 'S'
    bids = ['1S', 'P', '2D', 'P', '2S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '016'

def test_klinger_4_1_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('AJ2.J7.9743.A852')
    dealer = 'W'
    bids = ['P', '1NT', '2H', '4S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '020'

def test_klinger_4_2_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('K2.J843.K83.A964')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '023'

def test_klinger_4_2_ii_a():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('K2.J843.K83.A964')
    dealer = 'S'
    bids = ['1S', 'P', '2C', 'P', '3C', 'P', '4S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('C')
    assert suit.selection_reason == '026'

def test_klinger_4_2_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('K2.J843.K83.A964')
    dealer = 'S'
    bids = ['1H', 'P', '2C', 'P', '2S', 'P', '3H', 'P', '4H', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '014'

def test_klinger_4_3_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('83.9.KJ752.Q9843')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '008'

# def test_klinger_4_3_ii_a():
    # """Klinger exercise. Better Card play p24."""
#     hand = Hand('83.9.KJ752.Q9843')
#     dealer = 'S'
#     bids = ['1C', 'P', '1S', 'P', '2C', 'P', 'P', 'P']
#     board = _get_board(dealer, hand, bids)
#     suit = opening_lead_suit(board)

#     assert suit == Suit('D')  # not sure of reason for D!!!
#     assert suit.selection_reason == '026'

def test_klinger_4_3_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('83.9.KJ752.Q9843')
    dealer = 'S'
    bids = ['1H', 'P', '2C', 'P', '3C', 'P', '4H', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('C')
    assert suit.selection_reason == '026'

def test_klinger_4_4_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('AQ8.832.QJ72.843')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '027'

def test_klinger_4_4_ii_a():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('AQ8.832.QJ72.843')
    dealer = 'S'
    bids = ['1S', 'P', '1NT', 'P', '2H', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '028'

def test_klinger_4_4_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('AQ8.832.QJ72.843')
    dealer = 'S'
    bids = ['1C', 'P', '1D', 'P', '1H', 'P', '2H', 'P', '3H', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '028'

def test_klinger_4_5_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('KJ6.A975.2.KQ754')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('C')
    assert suit.selection_reason == '027'

def test_klinger_4_5_ii_a():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('KJ6.A975.2.KQ754')
    dealer = 'S'
    bids = ['1D', 'D', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '028'

def test_klinger_4_5_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('KJ6.A975.2.KQ754')
    dealer = 'S'
    bids = ['3H', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('C')
    assert suit.selection_reason == '027'

def test_klinger_4_6_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('98.AJ64.K763.873')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '028'

def test_klinger_4_6_ii_a():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('98.AJ64.K763.873')
    dealer = 'W'
    bids = ['P', '1C', 'P', '1S', 'P', '3C', 'P', '3S', '4S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '029'

def test_klinger_4_6_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('98.AJ64.K763.873')
    dealer = 'S'
    bids = ['1S', 'P', '1NT', 'P', '2H', 'P', '2S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('S')
    assert suit.selection_reason == '028'

def test_klinger_4_7_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('A8.7.K872.976432')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '008'

def test_klinger_4_7_ii_a():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('A8.7.K872.976432')
    dealer = 'S'
    bids = ['1S', 'P', '3S', 'P', '4NT', 'P', '5H', '6S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '030'

def test_klinger_4_7_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('A8.7.K872.976432')
    dealer = 'S'
    bids = ['1S', 'P', '3D', 'P', '4D', 'P', '4NT', 'P', '5H', '6S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('D')
    assert suit.selection_reason == '030'

def test_klinger_4_8_i():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('K2.86.QJT7.98642')
    bids = ['1S', 'P', '3S', 'P', '4S', 'P', 'P', 'P']
    board = _get_board('S', hand, bids)
    suit = opening_lead_suit(board)


    assert suit == Suit('D')
    assert suit.selection_reason == '002'

def test_klinger_4_8_ii_a():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('K2.86.QJT7.98642')
    dealer = 'N'
    bids = ['1C', 'P', '2S', 'P', '3S', 'P', '4NT', 'P', '5H', 'D', '6S', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('H')
    assert suit.selection_reason == '031'

def test_klinger_4_8_ii_b():
    """Klinger exercise. Better Card play p24."""
    hand = Hand('K2.86.QJT7.98642')
    dealer = 'N'
    bids = ['1C', 'P', '4NT', 'P', '5H', 'P', '6S', 'P', 'P', 'D', 'P', 'P', 'P']
    board = _get_board(dealer, hand, bids)
    suit = opening_lead_suit(board)

    assert suit == Suit('C')
    assert suit.selection_reason == '032'
