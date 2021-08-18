# PySide2
from PySide2 import QtWidgets, QtCore
# qasync
import qasync
# aioify
from aioify import aioify
# py-algorand-sdk
from algosdk.kmd import KMDClient
from algosdk.wallet import Wallet as AlgosdkWallet


# Tides
#   Miscellaneous
from algotides.interfaces.main.wallet.entities import Wallet
#   Interfaces
from algotides.interfaces.main.wallet.unlock.ui_window import Ui_UnlockWallet


class UnlockWallet(QtWidgets.QDialog, Ui_UnlockWallet):
    def __init__(
            self,
            parent: QtWidgets.QWidget,
            wallet: Wallet,
            kmd_client: KMDClient):
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.wallet = wallet
        self.kmd_client = kmd_client
        self.return_value = None

        self.setupUi(self)

        self.widget.setVisible(False)

    @qasync.asyncSlot()
    async def accept(self):
        self.lineEdit.setEnabled(False)
        self.widget.setVisible(True)
        self.buttonBox.setEnabled(False)

        try:
            self.return_value = await aioify(
                lambda: AlgosdkWallet(self.wallet.info["name"], self.lineEdit.text(), self.kmd_client),
            )()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Could not open wallet", str(e))
            self.return_value = None
            super().reject()
        else:
            super().accept()
