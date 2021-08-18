# Python
import decimal


# PySide2
from PySide2 import QtWidgets, QtCore, QtGui
# py-algorand-sdk
from algosdk.util import microalgos_to_algos, algos_to_microalgos


# Tides
#   Miscellaneous
from algotides.exceptions import TidesInvalidWidgetState
#   Interfaces
from algotides.interfaces.transaction.ui_linecombo_widget import Ui_TransactionLineCombo


class TransactionLineCombo(QtWidgets.QWidget, Ui_TransactionLineCombo):
    """
    This widget implements some common functionality for TransactionWindow.
    This widget is composed of a lineEdit and a comboBox and this pair can express an amount in Algos, microAlgos or
        just a positive integer (useful for getting back a quantity for an ASA).
    Number format is enforced by RegExp QValidators and automatically converted as the comboBox changes.
    """
    validators = {
        "decimal": QtGui.QRegExpValidator(QtCore.QRegExp(r"[0-9]+(\.[0-9]+)?")),
        "integer": QtGui.QRegExpValidator(QtCore.QRegExp(r"[0-9]+"))
    }

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        # Anti leak
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setupUi(self)

        # Default comboBox value is "Algos" so we set the decimal reg exp validator.
        self.lineEdit.setValidator(TransactionLineCombo.validators["decimal"])

        # Connections
        self.comboBox.currentIndexChanged.connect(
            self.combobox_index_changed_slot
        )

    def combo_set_enabled(self, setting: bool):
        self.comboBox.setEnabled(setting)
        self.lineEdit.setValidator(
            TransactionLineCombo.validators["decimal"] if (setting and self.comboBox.currentIndex() == 0)
            else TransactionLineCombo.validators["integer"]
        )

    def set_microalgos(self, n: int):
        conversion = {
            0: microalgos_to_algos,
            1: lambda x: x
        }

        if not self.comboBox.isEnabled():
            raise TidesInvalidWidgetState("Method was called when the comboBox is disabled.")

        self.lineEdit.setText(
            str(conversion[self.comboBox.currentIndex()](n))
        )

    def get_microalgos(self) -> int:
        conversion = {
            0: algos_to_microalgos,
            1: lambda x: int(x)
        }

        if not self.comboBox.isEnabled():
            raise TidesInvalidWidgetState("Method was called when the comboBox is disabled.")

        return conversion[self.comboBox.currentIndex()](
            decimal.Decimal(self.lineEdit.text())
        )

    # Unfortunately in this slot we can't use self.get_microalgos() because this slot is executed after the change
    #   in the currentIndex. Therefore the value in self.lineEdit would be interpreted incorrectly.
    @QtCore.Slot(int)
    def combobox_index_changed_slot(self, new_index: int):
        behaviours = {
            0: ("decimal", microalgos_to_algos),
            1: ("integer", algos_to_microalgos)
        }

        self.lineEdit.setValidator(
            TransactionLineCombo.validators[
                behaviours[new_index][0]
            ]
        )

        try:
            self.lineEdit.setText(str(
                behaviours[new_index][1](
                    decimal.Decimal(self.lineEdit.text())
                )
            ))
        except:
            # If we didn't manage to correctly interpret self.lineEdit.text() we fail silently because there was
            #   nothing to convert to begin with.
            pass
