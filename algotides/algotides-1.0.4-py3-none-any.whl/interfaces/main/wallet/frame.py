"""
This file contains WalletFrame which is a QFrame that is displayed inside MainWindow.
"""


# Python
import asyncio
import functools


# PySide2
from PySide2 import QtWidgets, QtCore, QtGui
# qasync
import qasync
# aioify
from aioify import aioify
# py-algorand-sdk
from algosdk.kmd import KMDClient
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.mnemonic import to_master_derivation_key


# Tides
#   Miscellaneous
from algotides.interfaces.main.wallet.entities import Wallet
#   Interfaces
from algotides.interfaces.main.wallet.ui_frame import Ui_WalletFrame
from algotides.interfaces.main.wallet.unlock.window import UnlockWallet
from algotides.interfaces.main.wallet.newimport.window import NewImportWallet
from algotides.interfaces.main.wallet.widgets import WalletListItem, WalletListWidget
from algotides.interfaces.main.address.frame import AddressFrame


class WalletsFrame(QtWidgets.QFrame, Ui_WalletFrame):
    """
    This class is the frame for the list of wallet in an Algorand node and the action on those wallets.
    """
    def __init__(
            self,
            parent: QtWidgets.QWidget,
            kmd_client: KMDClient,
            algod_client: AlgodClient,
            indexer_client: IndexerClient):
        super().__init__(parent)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.kmd_client = kmd_client
        self.algod_client = algod_client
        self.indexer_client = indexer_client

        self.setupUi(self)

        self.listWidget.set_item_type(WalletListItem)
        self.listWidget.activate_timer()

        # Connections
        self.listWidget.itemDoubleClicked.connect(self.manage_wallet)
        self.pushButton_Manage.clicked.connect(self.manage_wallet)
        self.pushButton_LockUnlock.clicked.connect(self.lock_unlock_wallet)
        self.pushButton_Rename.clicked.connect(self.rename_wallet)
        self.pushButton_NewImport.clicked.connect(self.new_import_wallet)
        self.pushButton_Export.clicked.connect(self.export_wallet)

        QtCore.QTimer.singleShot(0, self.restart)

    @qasync.asyncSlot()
    async def restart(self):
        if self.kmd_client:
            self.listWidget.activate_timer()

            try:
                wallets = await aioify(self.kmd_client.list_wallets)()
            except Exception as e:
                self.listWidget.clear_loading()

                QtWidgets.QMessageBox.critical(self, "Error: KMD Daemon - Load Wallets", str(e))
            else:
                for wallet in wallets:
                    self.listWidget.add_widget(
                        # Yikes...
                        WalletListWidget(Wallet(wallet))
                    )

                # Enable widgets that allow operation on an active node
                for widget in [self.pushButton_NewImport]:
                    widget.setEnabled(True)

                # Also enable widgets that only make sense for the existence of at least one wallet.
                if len(wallets) >= 1:
                    self.listWidget.setCurrentRow(0)

                    for widget in [self.pushButton_Manage, self.pushButton_LockUnlock, self.pushButton_Rename,
                                   self.pushButton_Export, self.parent().parent().parent().menuAction_NewTransaction]:
                        widget.setEnabled(True)
        else:
            QtWidgets.QMessageBox.critical(self, "Error: KMD Daemon - Settings",
                                           "Could not connect to an online KMD daemon.\n")

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == int(QtCore.Qt.Key_Return) and self.listWidget.hasFocus():
            self.manage_wallet()

    @qasync.asyncSlot()
    async def manage_wallet(self, item: WalletListItem = None):
        """
        This method opens up the AddressFrame of a given wallet.
        """
        if not item:
            item = self.listWidget.currentItem()

        if await self.unlock_item(item):
            widget = self.listWidget.itemWidget(item)

            self.parent().parent().parent().queuedWidget.add_widget(
                AddressFrame(self.parent(), widget.wallet, self.algod_client)
            )

    @qasync.asyncSlot()
    async def rename_wallet(self):
        item = self.listWidget.currentItem()

        if await self.unlock_item(item):
            widget = self.listWidget.itemWidget(item)

            new_name = QtWidgets.QInputDialog.getText(
                self, "Rename", "New name",
                QtWidgets.QLineEdit.EchoMode.Normal,
                widget.wallet.info["name"]
            )
            if new_name[1]:
                try:
                    # TODO Maybe this is a good time to use monadic error handling?
                    await aioify(lambda: widget.wallet.algo_wallet.rename(new_name[0]))()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Could not rename", str(e))
                else:

                    try:
                        widget.wallet.info = await aioify(widget.wallet.algo_wallet.info)()
                    except Exception as e:
                        QtWidgets.QMessageBox.critical(self, "Could not re-load wallets", str(e))
                    else:

                        widget.wallet.info = widget.wallet.info["wallet"]
                        widget.label_primary.setText(new_name[0])

    @qasync.asyncSlot()
    async def new_import_wallet(self):
        # TODO when importing a wallet ask the user how many addresses must be recovered.
        input_dialog = NewImportWallet(self)

        if input_dialog.exec_() == QtWidgets.QDialog.Accepted:
            try:
                # I never managed to aioify this call.
                new_wallet = await asyncio.get_event_loop().run_in_executor(
                    None,
                    functools.partial(
                        self.kmd_client.create_wallet,
                        input_dialog.return_value[0],
                        input_dialog.return_value[1],
                        master_deriv_key=(
                            to_master_derivation_key(input_dialog.return_value[2])
                            if input_dialog.return_value[2] != ""
                            else None
                        )
                    )
                )
            except Exception as e:
                if __debug__:
                    print(type(e), e)
                QtWidgets.QMessageBox.critical(self, "Could not create wallet", str(e))
            else:
                self.listWidget.add_widget(
                    WalletListWidget(
                        Wallet(new_wallet)
                    )
                )

    @qasync.asyncSlot()
    async def export_wallet(self):
        item = self.listWidget.currentItem()

        if await self.unlock_item(item):
            widget = self.listWidget.itemWidget(item)

            try:
                mnemonic_mdk = await aioify(widget.wallet.algo_wallet.get_mnemonic)()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Could not export wallet", str(e))
            else:
                QtGui.QGuiApplication.clipboard().setText(mnemonic_mdk)
                QtWidgets.QMessageBox.information(
                    self, "Success", "Mnemonic master derivation key copied into clipboard."
                )

    @qasync.asyncSlot()
    async def lock_unlock_wallet(self):
        """
        This method unlocks a locked item and viceversa.
        """
        item = self.listWidget.currentItem()
        widget = self.listWidget.itemWidget(item)

        if widget.wallet.algo_wallet:
            self.lock_item(item)
        else:
            await self.unlock_item(item)

    async def unlock_item(self, item: WalletListItem) -> bool:
        """
        This method takes an item with a misc.Entities.Wallet and creates an algosdk.wallet.Wallet creating a point for
        managing the kmd wallet.

        This method returns true if the wallet is already unlocked otherwise it tries to unlock it.
        """
        widget = self.listWidget.itemWidget(item)

        if widget.wallet.algo_wallet:
            return True

        unlocking_window = UnlockWallet(self, widget.wallet, self.kmd_client)

        if await aioify(unlocking_window.exec_)() == QtWidgets.QDialog.Accepted:
            widget.wallet.algo_wallet = unlocking_window.return_value
            widget.set_locked(False)
            return True

        return False

    def lock_item(self, item: WalletListItem):
        """
        This methods destroys the algosdk.wallet.Wallet object saved inside Entities.Wallet and marks the corresponding
        widget as locked.
        """
        widget = self.listWidget.itemWidget(item)

        widget.wallet.lock()
        widget.set_locked(True)
