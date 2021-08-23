"""A set of tests for the bridgeobjects pbn file format."""
import datetime
import pytest
from ..source.file_operations import load_rbn, save_pbn, load_pbn
from ..source.card import Card

DATA_PATH = 'test_data/'
LOAD_PATH = ''.join([DATA_PATH, 'pbn_input_file_1.pbn'])
events_loaded = load_pbn(LOAD_PATH)

# Create a pbn file from a rbn input to test saves
INPUT_PATH = ''.join([DATA_PATH, 'rbn_input_file_1.rbn'])
SAVE_PATH = ''.join([DATA_PATH, 'pbn_output_file_1.pbn'])
rbn_events = load_rbn(INPUT_PATH)
save_pbn(rbn_events, SAVE_PATH)
events_saved = load_pbn(SAVE_PATH)


def test_file_not_found():
    """Ensure file not found raises error."""
    with pytest.raises(FileNotFoundError):
        load_rbn('invalid_path')


@pytest.mark.parametrize("events, expected", [
    (events_loaded, 2),
    (events_saved, 2)
])
def test_event_counts(events, expected):
    """Ensure that the correct number of events are loaded and saved."""
    assert len(events) == expected


@pytest.mark.parametrize("event, expected", [
    (events_loaded[0], 27),
    (events_saved[0], 1)
])
def test_pbn_board_counts(event, expected):
    """Ensure that the number of boards created is correct."""
    assert len(event.boards) == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], 8),
    (events_saved[0].boards[0], 8)
])
def test_pbn_hands_counts(board, expected):
    """Ensure that the number of hands created is correct."""
    assert len(board.hands) == expected


@pytest.mark.parametrize("event, expected", [
    (events_loaded[0], "Monday afternoon"),
    (events_loaded[1], "Tuesday afternoon"),
    (events_saved[0], "ACBL International Fund Game"),
    (events_saved[1], "Second event")
])
def test_pbn_event_load_name(event, expected):
    """Ensure that the event is created correctly: name."""
    assert event.name == expected


@pytest.mark.parametrize("event, expected", [
    (events_loaded[0], "Utopia Bridge Club"),
    (events_saved[0], "West Palm Beach FL:Palm Beach Bridge Studio")
])
def test_pbn_event_load_location(event, expected):
    """Ensure that the event is created correctly: location."""
    assert event.location == expected


@pytest.mark.parametrize("event, expected", [
    (events_loaded[0], datetime.date(2018, 2, 26)),
    (events_saved[0], datetime.date(1993, 5, 12))
])
def test_pbn_event_load_date(event, expected):
    """Ensure that the event is created correctly: date."""
    assert event.date == expected


@pytest.mark.parametrize("event, expected", [
    (events_loaded[0], "MP"),
    (events_saved[0], "M")
])
def test_pbn_board_scoring_method(event, expected):
    """Ensure that the board is constructed correctly: scoring method."""
    assert event.scoring_method == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "4"),
    (events_saved[0].boards[0], "8")
])
def test_pbn_board_identifier(board, expected):
    """Ensure that the board is constructed correctly: identifier."""
    assert board.identifier == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "John Doe"),
    (events_saved[0].boards[0], "Wolff")
])
def test_pbn_board_north(board, expected):
    """Ensure that the board is constructed correctly: north."""
    assert board.north == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "A. N. Other"),
    (events_saved[0].boards[0], "Martel")
])
def test_pbn_board_east(board, expected):
    """Ensure that the board is constructed correctly: east."""
    assert board.east == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "Emma Royd"),
    (events_saved[0].boards[0], "Hamman")
])
def test_pbn_board_south(board, expected):
    """Ensure that the board is constructed correctly: south."""
    assert board.south == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "Joe Bloggs"),
    (events_saved[0].boards[0], "Stansby")
])
def test_pbn_board_west(board, expected):
    """Ensure that the board is constructed correctly: west."""
    assert board.west == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "Both"),
    (events_saved[0].boards[0], "None")
])
def test_pbn_board_vulnerable(board, expected):
    """Ensure that the board is constructed correctly: vulnerable."""
    assert board.vulnerable == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "S"),
    (events_saved[0].boards[0], "N")
])
def test_pbn_board_declarer(board, expected):
    """Ensure that the board is constructed correctly: declarer."""
    assert board.contract.declarer == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "5H"),
])
def test_pbn_board_contract(board, expected):
    """Ensure that the board is constructed correctly: contract."""
    assert board.contract.call.name == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[3], "D"),
])
def test_pbn_board_contract_doubled(board, expected):
    """Ensure that the board is constructed correctly: contract."""
    assert board.contract.modifier == expected


@pytest.mark.parametrize("board, expected", [
    (events_loaded[0].boards[12], "R"),
])
def test_pbn_board_contract_redoubled(board, expected):
    """Ensure that the board is constructed correctly: contract."""
    assert board.contract.modifier == expected


def test_pbn_board_hands():
    """Ensure that the board's hands are constructed correctly."""
    assert Card("6D") in events_loaded[0].boards[3].hands[3].cards
    assert Card("3D") in events_loaded[0].boards[3].hands[0].cards
    assert Card("9H") in events_loaded[0].boards[3].hands[1].cards
    assert Card("4S") in events_loaded[0].boards[3].hands[2].cards
    assert Card("6D") in events_loaded[0].boards[3].hands['W'].cards
    assert Card("3D") in events_loaded[0].boards[3].hands['N'].cards
    assert Card("9H") in events_loaded[0].boards[3].hands['E'].cards
    assert Card("4S") in events_loaded[0].boards[3].hands['S'].cards

    assert Card("7C") in events_saved[0].boards[0].hands[3].cards
    assert Card("7H") in events_saved[0].boards[0].hands[0].cards
    assert Card("5H") in events_saved[0].boards[0].hands[1].cards
    assert Card("9S") in events_saved[0].boards[0].hands[2].cards
    assert Card("7C") in events_saved[0].boards[0].hands['W'].cards
    assert Card("7H") in events_saved[0].boards[0].hands['N'].cards
    assert Card("5H") in events_saved[0].boards[0].hands['E'].cards
    assert Card("9S") in events_saved[0].boards[0].hands['S'].cards


def test_pbn_board_dealer():
    """
        Ensure that the board dealer is handled correctly.
        I.e. if the dealer is different from the seat marked
        with the first hand.
    """
    board = events_loaded[0].boards[20]
    assert board.identifier == "21"
    assert len(board.hands) == 8
    assert len(board.hands_by_seat) == 4
    assert len(board.hands_by_index) == 4
    assert repr(board) == f'Board("21", {board.hands_by_index})'
    assert board.dealer == "E"
    assert Card("KD") in board.hands[1].cards
    assert Card("7D") in board.hands[2].cards
    assert Card("9H") in board.hands[3].cards
    assert Card("4S") in board.hands[0].cards
    assert Card("KD") in board.hands['E'].cards
    assert Card("7D") in board.hands['S'].cards
    assert Card("9H") in board.hands['W'].cards
    assert Card("4S") in board.hands['N'].cards
