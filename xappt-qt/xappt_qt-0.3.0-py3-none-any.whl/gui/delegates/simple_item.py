from math import ceil

from PyQt5 import QtWidgets, QtCore


class SimpleItemDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hint_height = None

    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtCore.QSize:
        hint = super().sizeHint(option, index)
        if self._hint_height is None:
            self._hint_height = int(ceil(hint.height() * 1.5))
        hint.setHeight(self._hint_height)
        return hint
