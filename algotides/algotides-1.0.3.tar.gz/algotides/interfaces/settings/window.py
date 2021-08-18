"""
This file contains the SettingsWindow class and related static attributes and methods.
"""


# Python
from sys import stderr


# PySide2
from PySide2 import QtWidgets, QtCore


# Tides
#   Miscellaneous
from algotides.structures import DictJsonSettings
import algotides.serialization as serialization
import algotides.constants as constants
from algotides.exceptions import TidesBadEncoding
#   Interfaces
from algotides.interfaces.settings.ui_window import Ui_SettingsWindow


class SettingsWindow(QtWidgets.QDialog, Ui_SettingsWindow):
    jpickled_settings = None

    rest_endpoints = {}

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setupUi(self)

        # Setup interface
        pass

        # Setup logic
        QtCore.QTimer.singleShot(0, self.setup_logic)

    def setup_logic(self):
        # Alias.
        settings = SettingsWindow.jpickled_settings

        self.lineEdit_AlgodUrl.setText(settings["algod_url"])
        self.lineEdit_AlgodPort.setText(settings["algod_port"])
        self.lineEdit_AlgodToken.setText(settings["algod_token"])

        self.lineEdit_KmdUrl.setText(settings["kmd_url"])
        self.lineEdit_KmdPort.setText(settings["kmd_port"])
        self.lineEdit_KmdToken.setText(settings["kmd_token"])

    @QtCore.Slot()
    def accept(self):
        settings = SettingsWindow.jpickled_settings

        settings["algod_url"] = self.lineEdit_AlgodUrl.text()
        settings["algod_port"] = self.lineEdit_AlgodPort.text()
        settings["algod_token"] = self.lineEdit_AlgodToken.text()

        settings["kmd_url"] = self.lineEdit_KmdUrl.text()
        settings["kmd_port"] = self.lineEdit_KmdPort.text()
        settings["kmd_token"] = self.lineEdit_KmdToken.text()

        super().accept()

    @staticmethod
    def calculate_rest_endpoints() -> dict:
        """
        This static methods turns the user settings into REST connection points. Either by using manual mode or by
        reading it from algod.net, algod.token, kmd.net and kmd.token files.

        It's crucial that the pair (address, token) remains consistent. Meaning that either both exists or none does.
        """
        # Alias.
        settings = SettingsWindow.jpickled_settings

        endpoints = {}

        if settings["algod_url"] and settings["algod_port"] and settings["algod_token"]:
            endpoints["algod"] = {
                "address": "http://" + settings["algod_url"] + ':' + settings["algod_port"],
                "token": settings["algod_token"]
            }

        if settings["kmd_url"] and settings["kmd_port"] and settings["kmd_token"]:
            endpoints["kmd"] = {
                "address": "http://" + settings["kmd_url"] + ':' + settings["kmd_port"],
                "token": settings["kmd_token"]
            }

        return endpoints

    @staticmethod
    def initialize():
        if not constants.PATH_SETTINGS_JPICKLE.exists():
            serialization.dump_jpickle(constants.PATH_SETTINGS_JPICKLE, DictJsonSettings())

        SettingsWindow.jpickled_settings = serialization.load_jpickle(constants.PATH_SETTINGS_JPICKLE)

        if isinstance(SettingsWindow.jpickled_settings, DictJsonSettings):
            SettingsWindow.jpickled_settings.save_state()
        else:
            raise TidesBadEncoding(
                constants.PATH_SETTINGS_JPICKLE,
                type(SettingsWindow.jpickled_settings),
                type(DictJsonSettings())
            )

    @staticmethod
    def shut_down():
        if SettingsWindow.jpickled_settings.has_changed():
            try:
                serialization.dump_jpickle(
                    constants.PATH_SETTINGS_JPICKLE,
                    SettingsWindow.jpickled_settings
                )
            except IOError:
                print(f"Could not dump content into {constants.PATH_SETTINGS_JPICKLE}", file=stderr)
