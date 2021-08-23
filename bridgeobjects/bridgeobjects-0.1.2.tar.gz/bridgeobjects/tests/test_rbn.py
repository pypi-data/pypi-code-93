"""A set of tests for the bridgeobjects rbn file format."""
import pytest
import datetime
from ..source.card import Card
from ..source.call import Call
from ..source.file_operations import load_rbn, save_rbn, load_pbn

DATA_PATH = 'test_data/'
load_path = ''.join([DATA_PATH, 'rbn_input_file_1.rbn'])
events_loaded = load_rbn(load_path)
# event = events_loaded[0]
# board = event.boards[0]  # board 8

# Create a rbn file from a pbn input to test saves.
# The events are loaded from the pbn file at input_path to test_events.
input_path = ''.join([DATA_PATH, 'pbn_input_file_1.pbn'])
test_events = load_pbn(input_path)

# They are then saved in rbn format to a file at save_path.
save_path = ''.join([DATA_PATH, 'rbn_output_file_1.rbn'])
save_rbn(test_events, save_path)

# And reloaded to events_saved from save_path.
events_saved = load_rbn(save_path)

event = events_loaded[0]
board = event.boards[0]  # board 8

# board = 3
# hand = 1
# print('test_events ', test_events[0].boards[board].hands[hand])
# print('events_saved', events_saved[0].boards[board].hands[hand])
# print(test_events[0].boards[board].hands[hand].__str__() == events_saved[0].boards[board].hands[hand].__str__())
#
# print('QS ', events_saved[0].boards[3].hands[0].cards)


def test_rbn_event_counts():
    """Ensure that the number of events created is correct."""
    assert len(events_loaded) == 2


@pytest.mark.parametrize("events, expected", [
    (events_loaded, 2),
    (events_saved, 2)
])
def test_event_counts(events, expected):
    """Ensure all events are loaded."""
    assert len(events) == expected


@pytest.mark.parametrize("event, expected", [
    (events_loaded[0], 1),
    (events_saved[0], 27)
])
def test_pbn_board_counts(event, expected):
    """Ensure that the number of boards created is correct."""
    assert len(event.boards) == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[0], 8),
    (events_saved[0].boards[3], 8)
])
def test_pbn_hands_counts(board, expected):
    """Ensure that the number of hands created is correct."""
    assert len(board.hands) == expected


@pytest.mark.parametrize("event, expected", [
    (events_saved[0], "Monday afternoon"),
    (events_saved[1], "Tuesday afternoon"),
    (events_loaded[0], "ACBL International Fund Game"),
    (events_loaded[1], "Second event")
])
def test_pbn_event_load_name(event, expected):
    """Ensure that the event is created correctly: name."""
    assert event.name == expected


@pytest.mark.parametrize("event, expected", [
    (events_saved[0], "Utopia Bridge Club"),
    (events_loaded[0], "West Palm Beach FL:Palm Beach Bridge Studio")
])
def test_pbn_event_load_location(event, expected):
    """Ensure that the event is created correctly: location."""
    assert event.location == expected


@pytest.mark.parametrize("event, expected", [
    (events_saved[0], datetime.date(2018, 2, 26)),
    (events_loaded[0], datetime.date(1993, 5, 12))
])
def test_pbn_event_load_date(event, expected):
    """Ensure that the event is created correctly: date."""
    assert event.date == expected


def test_rbn_event_load_scoring_method():
    """Ensure that the event is created correctly: scoring method."""
    assert event.scoring_method == "M"


@pytest.mark.parametrize("board, expected", [
    (events_saved[0].boards[3], "4"),
    (events_loaded[0].boards[0], "8")
])
def test_pbn_board_identifier(board, expected):
    """Ensure that the board is constructed correctly: identifier."""
    assert board.identifier == expected


@pytest.mark.parametrize("board, expected", [
    (events_saved[0].boards[3], "John Doe"),
    (events_loaded[0].boards[0], "Wolff")
])
def test_pbn_board_north(board, expected):
    """Ensure that the board is constructed correctly: north."""
    assert board.north == expected


@pytest.mark.parametrize("board, expected", [
    (events_saved[0].boards[3], "Emma Royd"),
    (events_loaded[0].boards[0], "Hamman")
])
def test_pbn_board_south(board, expected):
    """Ensure that the board is constructed correctly: south."""
    assert board.south == expected


@pytest.mark.parametrize("board, expected", [
    (events_saved[0].boards[3], "Joe Bloggs"),
    (events_loaded[0].boards[0], "Stansby")
])
def test_pbn_board_west(board, expected):
    """Ensure that the board is constructed correctly: west."""
    assert board.west == expected


@pytest.mark.parametrize("board, expected", [
    (events_saved[0].boards[3], "A. N. Other"),
    (events_loaded[0].boards[0], "Martel")
])
def test_pbn_board_east(board, expected):
    """Ensure that the board is constructed correctly: east."""
    assert board.east == expected


@pytest.mark.parametrize("board, expected", [
    (events_saved[0].boards[3], "W"),
    (events_loaded[0].boards[0], "W")
])
def test_pbn_board_dealer(board, expected):
    """Ensure that the board is constructed correctly: dealer."""
    assert board.dealer == expected


@pytest.mark.parametrize("board, expected", [
    (events_saved[0].boards[3], "Both"),
    (events_loaded[0].boards[0], "None")
])
def test_pbn_board_vulnerable(board, expected):
    """Ensure that the board is constructed correctly: vulnerable."""
    assert board.vulnerable == expected


# @pytest.mark.parametrize("board, expected", [
# (events_saved[0].boards[3], "S"),
# (events_loaded[0].boards[0], "N")
# ])
# def test_pbn_board_declarer(board, expected):
# """Ensure that the board is constructed correctly: declarer."""
# assert board.declarer == expected

# @pytest.mark.parametrize("board, expected", [
# (events_saved[0].boards[3], "5HD"),
# (events_loaded[0].boards[0], "5HD")
# ])
# def test_pbn_board_contract(board, expected):
# """Ensure that the board is constructed correctly: contract."""
# assert board.contract == expected

def test_pbn_board_hands():
    """Ensure that the board's hands are constructed correctly."""
    assert Card("QS") in events_saved[0].boards[3].hands[0].cards, events_saved[0].boards[3].hands[0]
    assert Card("3C") in events_saved[0].boards[3].hands[1].cards, events_saved[0].boards[3].hands[1]
    assert Card("3H") in events_saved[0].boards[3].hands[2].cards, events_saved[0].boards[3].hands[2]
    assert Card("3S") in events_saved[0].boards[3].hands[3].cards, events_saved[0].boards[3].hands[3]

    assert Card("6C") in events_loaded[0].boards[0].hands[0].cards, events_saved[0].boards[0].hands[0]
    assert Card("TS") in events_loaded[0].boards[0].hands[1].cards, events_saved[0].boards[0].hands[1]
    assert Card("4H") in events_loaded[0].boards[0].hands[2].cards, events_saved[0].boards[0].hands[2]
    assert Card("8S") in events_loaded[0].boards[0].hands[3].cards, events_saved[0].boards[0].hands[3]


def test_rbn_board_auction():
    """Ensure that the board is constructed correctly: vulnerability."""
    calls = [Call('1S'), Call('2H'), Call('2S'), Call('4D'), Call('4S'),
             Call('P'), Call('P'), Call('5H'), Call('D'),
             Call('P'), Call('P'), Call('P')]
    assert board.auction.calls == calls
    assert repr(board) == f'Board("8", {board.hands_by_index})'


def test_rbn_board_hands():
    """Ensure that the board's hands are constructed correctly."""
    assert Card("7C") in board.hands[3].cards
    assert Card("7H") in board.hands[0].cards
    assert Card("5H") in board.hands[1].cards
    assert Card("9S") in board.hands[2].cards
    assert Card("7C") in board.hands['W'].cards
    assert Card("7H") in board.hands['N'].cards
    assert Card("5H") in board.hands['E'].cards
    assert Card("9S") in board.hands['S'].cards
