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

from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as n

from apav.qt import *

if TYPE_CHECKING:
    from apav import Roi


class QDecimalSpinBox(QDoubleSpinBox):
    # This signal only emits when editingFinished() produces a change in value
    editingFinishedAndChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.last_val = self.value()
        self.editingFinished.connect(self.onEditingFinished)

    def setValue(self, new):
        self.last_val = new
        super().setValue(new)

    def onEditingFinished(self):
        if n.isclose(self.last_val, self.value()):
            return
        else:
            self.last_val = self.value()
            self.editingFinishedAndChanged.emit()


class QMultiplicityComboBox(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)

    def formattedValue(self):
        """
        Get the multiplicity value in a format that APAV uses

        All = 'all'
        All multiples = 'multiples'

        Any integer is just converted to int
        Anything else raised an error
        """
        value = self.currentText()
        if value == "All":
            return "all"
        elif value == "All multiples":
            return "multiples"
        else:
            try:
                return int(value)
            except ValueError:
                raise ValueError("Invalid multiplicity value encountered in list")


class QMultiplesMultiplicityComboBox(QMultiplicityComboBox):
    def __init__(self, parent, roi: Roi):
        super().__init__(parent)

        roi.require_multihit_info()
        self.addItem("All multiples")
        for i in roi.multiplicities:
            if i > 1:
                self.addItem(str(i))


class QAnyMultiplicityComboBox(QMultiplicityComboBox):
    def __init__(self, parent, roi: Roi):
        super().__init__(parent)

        self.addItem("All")
        if roi.has_multiplicity_info():
            self.addItem("All multiples")
            for i in roi.multiplicities:
                self.addItem(str(i))
