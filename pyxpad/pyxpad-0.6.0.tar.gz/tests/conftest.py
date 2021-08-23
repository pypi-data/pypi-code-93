import numpy as np
import pytest
import shutil
from typing import Union
import pathlib

from pyxpad.pyxpad_utils import XPadDataDim, XPadDataItem
from pyxpad import xpadsource, PyXPad
from pyxpad.mock_data import MockClient


@pytest.fixture
def test_data():
    return {
        "name": "test data",
        "source": "test",
        "label": "some test data",
        "units": "m",
        "desc": "this is some test data",
        "data": np.array([-4.0, 5.0, 6.0]),
        "dim": [
            XPadDataDim(
                {"name": "dim1", "units": "m", "data": np.array([1.0, 2.0, 3.0])}
            )
        ],
        "errl": np.array([-4.5, 4.5, 6.5]),
        "errh": np.array([-3.2, 5.2, 6.2]),
    }


@pytest.fixture
def copy_tree_data(tmp_path):
    tree_path = "tree_data"
    dest = tmp_path / tree_path
    shutil.copytree(pathlib.Path(__file__).parent / tree_path, dest)
    return dest


class MockIdamModule:
    """Mock UDA module"""

    Client = MockClient


@pytest.fixture
def mock_uda(monkeypatch):
    monkeypatch.setattr(xpadsource, "has_uda", True)
    monkeypatch.setattr(xpadsource, "idam", MockIdamModule)


@pytest.fixture
def pyxpadbot(monkeypatch, qtbot):
    monkeypatch.setattr(PyXPad, "closeEvent", lambda self, event: event.accept())

    main = PyXPad(ignoreconfig=True)
    main.show()
    qtbot.add_widget(main)
    # I don't understand why I need to do this... qtbot seems to be
    # preserving state between tests?!
    main.sources.sources = []

    yield main
