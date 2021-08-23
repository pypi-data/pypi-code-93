from pyxpad.xpadsource import XPadSource
from Qt import QtCore

from pyxpad.mock_data import MOCK_LAST_SHOT

import pytest


def test_make_unique(qtbot, pyxpadbot):
    main = pyxpadbot

    assert main.makeUnique("def") == "def2"
    assert main.makeUnique("XMC_OMV/110") == "XMC_OMV_110"

    main.data["XMC_OMV_110"] = None
    assert main.makeUnique("XMC_OMV/110") == "XMC_OMV_110_1"
    main.data["XMC_OMV_110_1"] = None
    main.data["XMC_OMV_110_2"] = None
    assert main.makeUnique("XMC_OMV/110") == "XMC_OMV_110_3"


def test_get_last_shot(mock_uda, copy_tree_data, pyxpadbot, qtbot):
    main = pyxpadbot

    main.sources.addSource(XPadSource.from_tree(copy_tree_data))
    main.sources.updateDisplay()
    main.lastShotButton.setEnabled(True)
    qtbot.mouseClick(main.lastShotButton, QtCore.Qt.LeftButton)
    assert str(main.shotInput.text()).strip() == MOCK_LAST_SHOT


def test_get_last_shot_no_source(mock_uda, pyxpadbot, qtbot):
    main = pyxpadbot

    main.lastShotButton.setEnabled(True)
    qtbot.mouseClick(main.lastShotButton, QtCore.Qt.LeftButton)
    assert str(main.shotInput.text()).strip() == MOCK_LAST_SHOT


def test_get_available_signals(mock_uda, pyxpadbot, qtbot):
    main = pyxpadbot

    main.getAvailableSignalsButton.setEnabled(True)
    qtbot.mouseClick(main.getAvailableSignalsButton, QtCore.Qt.LeftButton)

    assert main.treeView.topLevelItemCount() == 1
    assert main.shotInput.text() == MOCK_LAST_SHOT
    main.treeView.topLevelItem(0).setSelected(True)

    assert main.sourceTable.rowCount() == 3
    assert main.sourceTable.item(0, 0).text() == "first_signal"

    # Clicking again shouldn't add more sources
    qtbot.mouseClick(main.getAvailableSignalsButton, QtCore.Qt.LeftButton)
    assert main.treeView.topLevelItemCount() == 1

    qtbot.keyClicks(main.shotInput, ", 66")
    qtbot.mouseClick(main.getAvailableSignalsButton, QtCore.Qt.LeftButton)
    assert main.treeView.topLevelItemCount() == 2
    qtbot.mouseClick(main.getAvailableSignalsButton, QtCore.Qt.LeftButton)
    assert main.treeView.topLevelItemCount() == 2
