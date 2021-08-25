# -*- coding: utf-8 -*-

#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2017  The IPMSim collaboration <http://ipmsim.gitlab.io/IPMSim>
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

from __future__ import absolute_import, unicode_literals

try:
    import PyQt4
except ImportError:
    try:
        import PyQt5
    except ImportError:
        raise ImportError('Either PyQt4 or PyQt5 is required')
    else:
        _IS_PyQt4 = False
        import PyQt5.QtCore as QtCore
        import PyQt5.QtGui as QtGui
        import PyQt5.QtWidgets as Widgets
else:
    _IS_PyQt4 = True
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
    import PyQt4.QtGui as Widgets

if _IS_PyQt4:
    import matplotlib.backends.backend_qt4agg as matplotlib_backend_qtXagg
else:
    import matplotlib.backends.backend_qt5agg as matplotlib_backend_qtXagg


# noinspection PyPep8Naming
def currentDataAsObject(widget):
    if _IS_PyQt4:
        return widget.itemData(widget.currentIndex()).toPyObject()
    else:
        return widget.currentData()


# noinspection PyShadowingBuiltins,PyPep8Naming,PyArgumentList
def getOpenFileName(parent=None, caption='', directory='', filter='', initialFilter='',
                    selectedFilter='', options=0):
    if _IS_PyQt4:
        return Widgets.QFileDialog.getOpenFileName(
            parent=parent, caption=caption, directory=directory, filter=filter,
            selectedFilter=selectedFilter, options=Widgets.QFileDialog.Options(options)
        )
    else:
        return Widgets.QFileDialog.getOpenFileName(
            parent=parent, caption=caption, directory=directory, filter=filter,
            initialFilter=initialFilter, options=Widgets.QFileDialog.Options(options)
        )[0]


# noinspection PyShadowingBuiltins,PyPep8Naming,PyArgumentList
def getSaveFileName(parent=None, caption='', directory='', filter='', initialFilter='',
                    selectedFilter='', options=0):
    if _IS_PyQt4:
        return Widgets.QFileDialog.getSaveFileName(
            parent=parent, caption=caption, directory=directory, filter=filter,
            selectedFilter=selectedFilter, options=Widgets.QFileDialog.Options(options)
        )
    else:
        return Widgets.QFileDialog.getSaveFileName(
            parent=parent, caption=caption, directory=directory, filter=filter,
            initialFilter=initialFilter, options=Widgets.QFileDialog.Options(options)
        )[0]
