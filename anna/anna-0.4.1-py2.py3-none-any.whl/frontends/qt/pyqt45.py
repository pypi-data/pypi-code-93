# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
