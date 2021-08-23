from pyxpad.pyxpad import Sources, PyXPad
from Qt import QtCore
from Qt.QtWidgets import QFileDialog

import pytest


@pytest.fixture
def setup_signal(copy_tree_data, mock_uda, qtbot, monkeypatch, pyxpadbot):
    main = pyxpadbot

    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory", lambda *args: copy_tree_data
    )
    main.actionXPAD_tree.trigger()
    main.treeView.topLevelItem(0).setSelected(True)

    return main


def test_add_XPad_source(setup_signal):
    main = setup_signal

    assert len(main.sources.sources) == 1
    assert main.treeView.topLevelItemCount() == 1

    assert main.sourceTable.rowCount() == 5


def test_delete_source(setup_signal):
    main = setup_signal

    main.sources.actionDelete.trigger()
    assert main.treeView.topLevelItemCount() == 0
    assert main.sourceTable.rowCount() == 0


def test_source_description(setup_signal, qtbot):
    main = setup_signal
    qtbot.mouseClick(main.sourceDescription, QtCore.Qt.LeftButton)

    assert main.sourceTable.columnCount() == 2
    assert main.sourceTable.item(1, 1).text() == "a description"


def test_filter_trace(setup_signal, qtbot):
    main = setup_signal
    qtbot.keyClicks(main.tracePattern, "signal_*")
    qtbot.keyClick(main.tracePattern, QtCore.Qt.Key_Return)
    assert main.sourceTable.rowCount() == 3


def test_filter_available_signals(setup_signal, qtbot):
    main = setup_signal
    qtbot.mouseClick(main.availableSignals, QtCore.Qt.LeftButton)

    assert main.sourceTable.rowCount() == 3
    assert main.sourceTable.item(0, 0).text() == "first_signal"

    qtbot.keyClicks(main.shotInput, "66")
    qtbot.mouseClick(main.availableSignals, QtCore.Qt.LeftButton)
    qtbot.mouseClick(main.availableSignals, QtCore.Qt.LeftButton)
    assert main.sourceTable.rowCount() == 4
    assert main.sourceTable.item(0, 0).text() == "second_signal"

    qtbot.keyClicks(main.shotInput, "66, 45321, 12354")
    qtbot.mouseClick(main.availableSignals, QtCore.Qt.LeftButton)
    qtbot.mouseClick(main.availableSignals, QtCore.Qt.LeftButton)
    assert main.sourceTable.rowCount() == 1
    assert main.sourceTable.item(0, 0).text() == "signal_b"


def test_filter_pattern(setup_signal, qtbot):
    main = setup_signal
    qtbot.keyClicks(main.tracePattern, "signal_*")
    assert main.sourceTable.rowCount() == 3
    assert main.sourceTable.item(0, 0).text() == "signal_a"
