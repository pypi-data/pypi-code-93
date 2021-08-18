# Python
import decimal
from textwrap import wrap


# PySide2
from PySide2 import QtWidgets, QtCore
# py-algorand-sdk
from algosdk.util import microalgos_to_algos


# Tides
#   Interfaces
from algotides.interfaces.main.address.balance.ui_window import Ui_BalanceWindow
from algotides.interfaces.main.address.widgets import BalanceScrollWidget


# TODO: Use the same grouping of integers for asset amount.
class BalanceWindow(QtWidgets.QDialog, Ui_BalanceWindow):
    """
    This class implements the balance window. It displays current balance, pending rewards and assets.
    """
    def __init__(self, parent: QtWidgets.QWidget, account_info: dict):
        super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        # Anti memory leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.account_info = account_info

        self.setupUi(self)

        def format_microalgos(n: int) -> str:
            def group_integer(k: int) -> str:
                tokens = wrap(str(k), 3)
                output = tokens[-1]

                for token in tokens[:-1]:
                    output += token + ","

                return output

            temp1 = decimal.Decimal(microalgos_to_algos(n))

            integer, fractional = int(temp1 // decimal.Decimal(1)), temp1 % decimal.Decimal(1)
            return group_integer(integer) + (f".{str(fractional)[2:]}" if fractional != 0 else "") + " Algos"

        self.label_Balance.setText(
            format_microalgos(account_info["amount-without-pending-rewards"])
        )
        self.label_Pending.setText(
            format_microalgos(account_info["pending-rewards"])
        )

        for asset in account_info["assets"]:
            self.verticalLayout_assets.addWidget(
                BalanceScrollWidget(
                    f"{asset['asset-id']}",
                    f"{asset['amount']}"
                )
            )
        self.verticalLayout_assets.addStretch(1)
