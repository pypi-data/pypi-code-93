from pyxpad.xpadsource import XPadSource
from pyxpad.pyxpad_utils import XPadDataDim, XPadDataItem
from pyxpad.mock_data import MOCK_LAST_SHOT, MOCK_SIGNALS


EXPECTED_VARIABLE_NAMES = [signal[0] for signal in MOCK_SIGNALS]


def test_init_with_tree(copy_tree_data):
    source = XPadSource.from_tree(copy_tree_data)

    assert list(source.variables.keys()) == EXPECTED_VARIABLE_NAMES
    assert source.variables["second_signal"].desc == "a description"


def test_read(copy_tree_data, mock_uda):
    source = XPadSource.from_tree(copy_tree_data)

    data = source.read("something", 42)
    assert data.name == "something"


def test_latest_shot(mock_uda):
    source = XPadSource()
    assert source.last_shot_number == int(MOCK_LAST_SHOT)


def test_from_signals(mock_uda):
    source = XPadSource.from_signals(1)
    assert list(source.variables.keys()) == EXPECTED_VARIABLE_NAMES
