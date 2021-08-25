from collections import deque
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

from xappt import BaseTool

from xappt_qt.gui.widgets import ToolPage
from xappt_qt.gui.ui.runner import Ui_RunDialog
from xappt_qt import config
from xappt_qt.constants import APP_TITLE

# noinspection PyUnresolvedReferences
from xappt_qt.gui.resources import icons


class RunDialog(QtWidgets.QDialog, Ui_RunDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.set_window_attributes()

        self.tool_plugin: Optional[BaseTool] = None
        self.tool_widget: Optional[ToolPage] = None

        self._console_lines = deque(maxlen=config.console_line_limit)

        self.init_ui()

    def set_window_attributes(self):
        flags = QtCore.Qt.Window
        flags |= QtCore.Qt.WindowCloseButtonHint
        flags |= QtCore.Qt.WindowMinimizeButtonHint
        self.setWindowFlags(flags)
        self.setWindowIcon(QtGui.QIcon(":appicon"))

    def init_ui(self):
        self.placeholder.setVisible(False)

        # noinspection PyArgumentList
        font_size = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.GeneralFont).pointSizeF()
        # noinspection PyArgumentList
        mono_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        mono_font.setPointSizeF(font_size)
        self.txtOutput.setFont(mono_font)

        self.hide_console()

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.clear()
        return super().closeEvent(event)

    def show_console(self):
        half_height = int(self.height() * 0.5)
        self.splitter.setSizes((half_height, half_height))

    def hide_console(self):
        self.splitter.setSizes((self.height(), 0))

    def is_console_visible(self) -> bool:
        return self.txtOutput.isVisible()

    def clear_console(self):
        self._console_lines.clear()
        self.txtOutput.clear()

    def clear(self):
        if self.tool_widget is not None:
            self.tool_widget.disconnect()
            index = self.gridLayout.indexOf(self.tool_widget)
            self.gridLayout.takeAt(index)
            self.tool_widget.deleteLater()
            self.tool_widget = None
            self.tool_plugin = None
        self.btnOk.setEnabled(True)

    def set_current_tool(self, tool_plugin: BaseTool):
        if self.tool_widget is not None:
            raise RuntimeError("Clear RunDialog before adding a new tool.")
        self.tool_plugin = tool_plugin
        self.tool_widget = ToolPage(self.tool_plugin)
        self.gridLayout.addWidget(self.tool_widget, 0, 0)
        self.setWindowTitle(f"{tool_plugin.name()} - {APP_TITLE}")
        self.tool_widget.setEnabled(True)

    @staticmethod
    def convert_leading_whitespace(s: str, tabwidth: int = 4) -> str:
        leading_spaces = 0
        while True:
            if not len(s):
                break
            if s[0] == " ":
                leading_spaces += 1
            elif s[0] == "\t":
                leading_spaces += tabwidth
            else:
                break
            s = s[1:]
        return f"{'&nbsp;' * leading_spaces}{s}"

    def add_output_line(self, s: str, error: bool = False):
        s = self.convert_leading_whitespace(s)
        if error:
            self._console_lines.append(f'<span style="color: #f55">{s}</span>')
        else:
            self._console_lines.append(f'<span style="color: #ccc">{s}</span>')
        self.txtOutput.setHtml("<br />".join(self._console_lines))
        self.txtOutput.moveCursor(QtGui.QTextCursor.End)
        max_scroll = self.txtOutput.verticalScrollBar().maximum()
        self.txtOutput.verticalScrollBar().setValue(max_scroll)
        self.txtOutput.horizontalScrollBar().setValue(0)
        # noinspection PyArgumentList
        QtWidgets.QApplication.instance().processEvents()

    def add_error_line(self, s: str):
        self.add_output_line(s, True)
