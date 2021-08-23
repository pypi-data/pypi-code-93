from pyxpad.pyxpad_utils import XPadDataDim, XPadDataItem
from pyxpad.console_widget import ConsoleWidget
from Qt import QtCore


def test_console_widget(qtbot, capsys):
    def print_command(text):
        print(text)

    console = ConsoleWidget()
    console.show()
    console.commandEntered.connect(print_command)
    qtbot.add_widget(console)

    first_text = "some text"
    qtbot.keyClicks(console, first_text)
    qtbot.keyClick(console, QtCore.Qt.Key_Return)
    assert len(console.history) == 1
    assert console.history[0] == first_text

    second_text = "some more text"
    qtbot.keyClicks(console, second_text)
    qtbot.keyClick(console, QtCore.Qt.Key_Return)
    assert len(console.history) == 2
    assert console.history[0] == first_text
    assert console.history[1] == second_text

    captured = capsys.readouterr()
    assert captured.out == f"{first_text}\n{second_text}\n"


def test_console_widget_history(qtbot):
    console = ConsoleWidget()
    console.show()
    qtbot.add_widget(console)

    first_text = "some text"
    second_text = "some more text"
    qtbot.keyClicks(console, first_text)
    qtbot.keyClick(console, QtCore.Qt.Key_Return)
    qtbot.keyClicks(console, second_text)
    qtbot.keyClick(console, QtCore.Qt.Key_Return)

    qtbot.keyClick(console, QtCore.Qt.Key_Up)
    qtbot.keyClick(console, QtCore.Qt.Key_Up)

    assert console.history[console.current] == first_text
    assert console.text() == first_text

    qtbot.keyClick(console, QtCore.Qt.Key_Down)
    assert console.history[console.current] == second_text
    assert console.text() == second_text

    qtbot.keyClick(console, QtCore.Qt.Key_Down)
    assert console.current == 2
    assert console.text() == ""
