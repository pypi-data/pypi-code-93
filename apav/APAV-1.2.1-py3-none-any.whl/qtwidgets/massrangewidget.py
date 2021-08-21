"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""

from apav.qt import *
from apav.core.range import RangeCollection, Range


class QMassRangeWidget(QWidget):
    """
    A widget for navigating the ranges in RangeCollection
    """
    sigRangeDoubleClicked = pyqtSignal(Range)

    def __init__(self, parent, ranges: RangeCollection):
        super().__init__(parent)
        if not isinstance(ranges, RangeCollection):
            raise TypeError(f"Expected a RangeCollection not {type(ranges)}")
        self.ranges = ranges

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        self._view = QTreeView()
        self._view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._layout.addWidget(self._view)
        self._model = QStandardItemModel()
        self._view.setModel(self._model)

        _color_delg = RangeColorDelegate()
        self._view.setItemDelegateForColumn(0, _color_delg)
        self._view.setSelectionMode(QTreeView.NoSelection)

        self._model.setHorizontalHeaderLabels(["Ion", "Min", "Max"])

        for ion in self.ranges.ions():
            ion_item = QStandardItem(ion.hill_formula)
            ion_item.setEditable(False)

            for rngg in self.ranges:
                if ion.hill_formula == rngg.hill_formula:
                    rng_min = QStandardItem(str(rngg.lower))
                    rng_min.setData(rngg, Qt.UserRole)
                    rng_min.setEditable(False)

                    rng_max = QStandardItem(str(rngg.upper))
                    rng_max.setData(rngg, Qt.UserRole)
                    rng_max.setEditable(False)

                    rng_col = QStandardItem()
                    rng_col.setEditable(False)
                    rng_col.setData(rngg, Qt.UserRole)

                    ion_item.appendRow([rng_col, rng_min, rng_max])

            self._model.invisibleRootItem().insertRow(0, [ion_item, None, None])

        self._view.expandAll()

        self._view.setColumnWidth(0, 85)
        self._view.setColumnWidth(1, 75)
        self._view.setColumnWidth(2, 75)

        self._view.doubleClicked.connect(self._onDoubleClicked)

    def _onDoubleClicked(self, index: QModelIndex):
        rng_item = index.data(Qt.UserRole)
        if not index.isValid() or not isinstance(rng_item, Range):
            return

        self.sigRangeDoubleClicked.emit(rng_item)


class RangeColorDelegate(QStyledItemDelegate):
    """
    Delegate for displaying the color of a range
    """
    def paint(self, painter, option, index):
        if not index.isValid():
            super().paint(painter, option, index)
            return

        rng = index.data(Qt.UserRole)
        if not isinstance(rng, Range):
            super().paint(painter, option, index)
            return

        # Setup painter
        pen = QPen()
        pen.setWidth(0)
        painter.setPen(pen)
        color = rng.color
        brush = QBrush(QColor.fromRgbF(*color))
        painter.setBrush(brush)

        # Draw the rectangle
        height = option.rect.height()
        center = option.rect.center()
        rect = QRect(height, height, height, height)
        rect.moveCenter(center)
        painter.drawRect(rect)

        super().paint(painter, option, index)


