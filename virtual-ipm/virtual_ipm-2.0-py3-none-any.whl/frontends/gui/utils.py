#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Union

import PyQt5.QtWidgets as Widgets
from PyQt5.QtWidgets import QWidget, QLayout, QBoxLayout, QHBoxLayout, QVBoxLayout


# noinspection PyShadowingBuiltins,PyPep8Naming
def getOpenFileName(parent=None, caption='', directory='', filter='', initialFilter='', **kwargs):
    return Widgets.QFileDialog.getOpenFileName(
        parent=parent, caption=caption, directory=directory, filter=filter, initialFilter=initialFilter,
        **kwargs,
    )[0]


# noinspection PyShadowingBuiltins,PyPep8Naming
def getSaveFileName(parent=None, caption='', directory='', filter='', initialFilter='', **kwargs):
    return Widgets.QFileDialog.getSaveFileName(
        parent=parent, caption=caption, directory=directory, filter=filter, initialFilter=initialFilter,
        **kwargs,
    )[0]


def pad_hv(w: Union[QWidget, QLayout]) -> QLayout:
    return pad_v(pad_h(w))


def pad_h(w: Union[QWidget, QLayout]) -> QLayout:
    return pad(w, layout=QHBoxLayout())


def pad_v(w: Union[QWidget, QLayout]) -> QLayout:
    return pad(w, layout=QVBoxLayout())


def pad(w: Union[QWidget, QLayout], *, layout: QBoxLayout) -> QLayout:
    if isinstance(w, QLayout):
        add_func = layout.addLayout
    elif isinstance(w, QWidget):
        add_func = layout.addWidget
    else:
        raise TypeError(f'Cannot pad object of type {type(w)}')
    layout.addStretch(1)
    add_func(w)
    layout.addStretch(1)
    return layout
