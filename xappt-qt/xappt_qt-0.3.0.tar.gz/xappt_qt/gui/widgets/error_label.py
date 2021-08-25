from PyQt5 import QtWidgets

from xappt_qt.constants import *


class ErrorLabel(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self._message: str = ""
        self.linkActivated.connect(self._on_link_activated)

    def reset(self):
        self._message = ""
        self.setText("")

    def set_error(self, message: str):
        self._message = message
        self.setText('<a href="#" style="color: red; text-decoration:none; font-size: 14pt;">⛔</a>')

    def show_error(self):
        if len(self._message):
            QtWidgets.QMessageBox.critical(self.parent(), APP_TITLE, self._message)

    def _on_link_activated(self, _: str):
        self.show_error()
