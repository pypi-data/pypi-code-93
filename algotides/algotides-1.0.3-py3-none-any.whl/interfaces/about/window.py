"""
This file contains info window.

Things like author licences and outsourcing images.
These windows are made so that they fit the content rather than the content fits the dimention of the window.
"""


# Python
import functools

# PySide2
from PySide2 import QtWidgets, QtCore, QtGui

# Tides
#   Interfaces
from algotides.interfaces.about.info.ui_window import Ui_Info
from algotides.interfaces.about.credits.ui_window import Ui_Credits
from algotides.interfaces.about.donate.ui_window import Ui_Donate


class InfoWindow(QtWidgets.QDialog, Ui_Info):
    """
    This class is the info about this application window
    """
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setupUi(self)

        self.label_5.setPixmap(QtGui.QPixmap(":/logos/tides-resized.png"))


class CreditsWindow(QtWidgets.QDialog, Ui_Credits):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setupUi(self)


class DonateWindow(QtWidgets.QDialog, Ui_Donate):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setupUi(self)

        # Connections
        self.pushButton_Copy.clicked.connect(
            lambda: QtGui.QGuiApplication.clipboard().setText(self.lineEdit_DonateAddress.text())
        )
