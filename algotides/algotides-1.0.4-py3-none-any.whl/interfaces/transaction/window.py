"""
This file only contains TransactionWindow.
"""


# PySide2
from PySide2 import QtWidgets, QtCore, QtGui
# qasync
import qasync
# aioify
from aioify import aioify
# py-algorand-sdk
from algosdk.v2client.algod import AlgodClient
from algosdk import transaction
from algosdk.encoding import is_valid_address
from algosdk.future.transaction import SuggestedParams


# Tides
#   Miscellaneous
from algotides.exceptions import TidesBadTransactionField
#   Interfaces
from algotides.interfaces.transaction.ui_window import Ui_TransactionWindow
from algotides.interfaces.contacts.window import ContactsWindow


# TODO: Add a "Minimum fee" alongside "Suggested fee"
# TODO: use monospaced font to make all addresses long the same amount.
class TransactionWindow(QtWidgets.QDialog, Ui_TransactionWindow):
    """
    This class implements the transaction window.
    """
    def __init__(
            self,
            parent: QtWidgets.QWidget,
            wallet_frame: QtWidgets.QFrame,
            algod_client: AlgodClient):
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        self.wallet_frame = wallet_frame
        self.algod_client = algod_client

        self.setupUi(self)

        # Setup interface
        self.lineEdit_AssetId.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]+")))

        self.comboBox_Sender.addItem("Select a valid Algorand address from the unlocked wallets...")
        self.comboBox_Receiver.addItem("Type in a valid Algorand address or select one...")
        self.comboBox_CloseTo.addItem("Type in a valid Algorand address or select one...")

        # Connections
        self.checkBox_CloseTo.toggled.connect(self.checkbox_close_to_slot)
        self.comboBox_Type.currentIndexChanged.connect(self.combobox_type_slot)
        self.comboBox_AssetMode.currentIndexChanged.connect(self.combobox_asset_mode_slot)
        self.pushButton_SuggestedFee.clicked.connect(self.pushbutton_sf_slot)

        QtCore.QTimer.singleShot(0, self.restart)

    @qasync.asyncSlot()
    async def restart(self):
        # Alias.
        wallet_list = self.wallet_frame.listWidget

        # Load every address from ever unlocked wallet.
        for i in range(wallet_list.count()):
            item = wallet_list.item(i)
            widget = wallet_list.itemWidget(item)

            if widget.wallet.algo_wallet:
                for address in await aioify(widget.wallet.algo_wallet.list_keys)():
                    self.comboBox_Sender.addItem(f"{widget.wallet.info['name']} - {address}", widget.wallet.algo_wallet)
                    self.comboBox_Receiver.addItem(f"Wallet: {widget.wallet.info['name']} - {address}")
                    self.comboBox_CloseTo.addItem(f"Wallet: {widget.wallet.info['name']} - {address}")

        # Load every address from every contact.
        for contact in ContactsWindow.jpickled_contacts:
            self.comboBox_Receiver.addItem(f"Contact: {contact.name} - {contact.address}")
            self.comboBox_CloseTo.addItem(f"Contact: {contact.name} - {contact.address}")

    # I know these nested try blocks look horrifying. I swear someday I'm going to bring monadic
    #   error handling to Python.
    # Or I could avoid the else branch, write one block after the other if I remember to
    #   return in each "except" branch.
    @qasync.asyncSlot()
    async def accept(self):
        try:
            sp = await aioify(self.algod_client.suggested_params)()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Could not get suggested parameters", str(e))
        else:

            wallet = self.comboBox_Sender.currentData()
            try:
                txn = self.get_transaction(sp)
            except TidesBadTransactionField as e:
                QtWidgets.QMessageBox.critical(self, "Could not compile a correct transaction.", str(e))
            else:

                try:
                    signed_txn = await aioify(lambda: wallet.sign_transaction(txn))()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Could not sign transaction", str(e))
                else:

                    try:
                        txn_address = await aioify(lambda: self.algod_client.send_transaction(signed_txn))()
                    except Exception as e:
                        QtWidgets.QMessageBox.critical(self, "Could not send transaction", str(e))
                    else:
                        QtGui.QGuiApplication.clipboard().setText(txn_address)
                        QtWidgets.QMessageBox.information(self, "Transaction", "Transaction sent to the node.\n"
                                                                               "Transaction address copied into "
                                                                               "clipboard.")
                        super().accept()

        # If the user presses OK but the transaction is invalid we shouldn't close the QDialog.
        # super().reject()

    @QtCore.Slot()
    def checkbox_close_to_slot(self):
        if self.checkBox_CloseTo.isChecked():
            self.comboBox_CloseTo.setEnabled(True)
        else:
            self.comboBox_CloseTo.setEnabled(False)

    @QtCore.Slot(int)
    def combobox_type_slot(self, new_index: int):
        if new_index == 0:
            self.lineCombo_Amount.combo_set_enabled(True)

            for widget in [self.lineEdit_AssetId, self.comboBox_AssetMode]:
                widget.setEnabled(False)

            self.comboBox_AssetMode.setCurrentIndex(0)

        else:
            self.lineCombo_Amount.combo_set_enabled(False)

            for widget in [self.lineEdit_AssetId, self.comboBox_AssetMode]:
                widget.setEnabled(True)

    @QtCore.Slot(int)
    def combobox_asset_mode_slot(self, new_index: int):
        if new_index == 0:
            # Transfer
            for widget in [self.comboBox_Receiver, self.checkBox_CloseTo, self.lineCombo_Amount.lineEdit]:
                widget.setEnabled(True)
        else:
            # Opt-in
            for widget in [self.comboBox_Receiver, self.checkBox_CloseTo, self.lineCombo_Amount.lineEdit]:
                widget.setEnabled(False)

            self.checkBox_CloseTo.setChecked(False)

    @qasync.asyncSlot()
    async def pushbutton_sf_slot(self):
        """
        This method calculates the suggested fee for the whole transaction.

        This method compiles an unsigned transaction with the parameters and then uses .estimate_size() on
        the transaction. Then uses .suggested_params() from algod client to get fee per byte. Then it's easy math.
        """
        try:
            sp = await aioify(self.algod_client.suggested_params)()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Could not load suggested fee", str(e))
        else:
            # We have to do this because self.get_transaction() will raise an error if the fee field
            #   is not correct. Same thing if it's empty. We modify before calling because in this
            #   method we are supposed to change this field anyway.
            # Furthermore the fee can't get smaller than the minimum.
            old_value = self.lineCombo_Fee.lineEdit.text()
            self.lineCombo_Fee.set_microalgos(sp.min_fee)

            try:
                temp_txn = self.get_transaction(sp)
            except TidesBadTransactionField as e:
                self.lineCombo_Fee.lineEdit.setText(old_value)
                QtWidgets.QMessageBox.critical(self, "Could not calculate suggested fee", str(e))
            else:

                self.lineCombo_Fee.set_microalgos(
                    max(sp.min_fee, temp_txn.estimate_size() * sp.fee)
                )

    def get_transaction(self, sp: SuggestedParams) -> transaction.Transaction:
        txn_data = dict()

        # Just some "macro(s)" to avoid code duplication.
        def get_receiver():
            txn_data["receiver"] = self.comboBox_Receiver.currentText()[-58:]
            if not is_valid_address(txn_data["receiver"]):
                raise TidesBadTransactionField("Receiver", "Receiver was not a valid Algorand address.")

        def get_close_to():
            if self.checkBox_CloseTo.isChecked():
                txn_data["close_remainder_to"] = self.comboBox_CloseTo.currentText()[-58:]
                if not is_valid_address(txn_data["close_remainder_to"]):
                    raise TidesBadTransactionField("Close To", "Close To was not a valid Algorand address.")
        # End macros

        txn_data["sender"] = self.comboBox_Sender.currentText()[-58:]
        if not is_valid_address(txn_data["sender"]):
            raise TidesBadTransactionField("Sender", "Sender was not a valid Algorand address.")

        try:
            txn_data["fee"] = self.lineCombo_Fee.get_microalgos()
        except Exception as e:
            raise TidesBadTransactionField("Fee", "Field conversion to an amount in microAlgos was not possible.")
        else:

            if txn_data["fee"] < sp.min_fee:
                raise TidesBadTransactionField("Fee", "Fee was less than minimum fee.")

        txn_data["flat_fee"] = True
        txn_data["first"] = sp.first
        txn_data["last"] = sp.last
        txn_data["gh"] = sp.gh
        txn_data["note"] = self.textEdit_Note.toPlainText().encode()

        if self.comboBox_Type.currentIndex() == 0:
            # PaymentTxn.
            get_receiver()
            get_close_to()

            try:
                txn_data["amt"] = self.lineCombo_Amount.get_microalgos()
            except Exception as e:
                raise TidesBadTransactionField(
                    "Amount",
                    "Field conversion to an amount in microAlgos was not possible."
                )

            txn = transaction.PaymentTxn(**txn_data)
        else:
            # AssetTransferTxn.
            txn_data["index"] = int(self.lineEdit_AssetId.text())

            if self.comboBox_AssetMode.currentIndex() == 0:
                # ASA Transfer.
                get_receiver()
                get_close_to()

                try:
                    txn_data["amt"] = int(self.lineCombo_Amount.lineEdit.text())
                except Exception as e:
                    raise TidesBadTransactionField("Amount", "Field conversion to an amount was not possible.")
            elif self.comboBox_AssetMode.currentIndex() == 1:
                # ASA Opt-In.
                txn_data["receiver"] = txn_data["sender"]
                txn_data["amt"] = 0
            # Opt-Out case is taken care by the Close To check box.

            txn = transaction.AssetTransferTxn(**txn_data)

        return txn
