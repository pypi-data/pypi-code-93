# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import pyqt45

QtCore = pyqt45.QtCore
Widgets = pyqt45.Widgets


# noinspection PyPep8Naming
class Folder(Widgets.QWidget):
    """
    References
    ----------
    http://stackoverflow.com/a/37927256
    """

    def __init__(self, parent=None, title='', animationDuration=100):
        super(Folder, self).__init__(parent=parent)

        self.animationDuration = animationDuration
        self.toggleAnimation = QtCore.QParallelAnimationGroup()
        self.contentArea = Widgets.QScrollArea()
        self.headerLine = Widgets.QFrame()
        self.toggleButton = Widgets.QToolButton()
        self.mainLayout = Widgets.QGridLayout()

        toggleButton = self.toggleButton
        toggleButton.setStyleSheet("QToolButton { border: none; }")
        toggleButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        toggleButton.setArrowType(QtCore.Qt.RightArrow)
        toggleButton.setText(str(title))
        toggleButton.setCheckable(True)
        toggleButton.setChecked(False)

        headerLine = self.headerLine
        headerLine.setFrameShape(Widgets.QFrame.HLine)
        headerLine.setFrameShadow(Widgets.QFrame.Sunken)
        headerLine.setSizePolicy(Widgets.QSizePolicy.Expanding, Widgets.QSizePolicy.Maximum)

        self.contentArea.setStyleSheet("QScrollArea { border: none; }")
        self.contentArea.setSizePolicy(Widgets.QSizePolicy.Expanding, Widgets.QSizePolicy.Fixed)
        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)
        # let the entire widget grow and shrink with its content
        toggleAnimation = self.toggleAnimation
        toggleAnimation.addAnimation(
            QtCore.QPropertyAnimation(self, "minimumHeight".encode('ascii'))
        )
        toggleAnimation.addAnimation(
            QtCore.QPropertyAnimation(self, "maximumHeight".encode('ascii'))
        )
        toggleAnimation.addAnimation(
            QtCore.QPropertyAnimation(self.contentArea, "maximumHeight".encode('ascii'))
        )
        # don't waste space
        mainLayout = self.mainLayout
        mainLayout.setVerticalSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        row = 0
        mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(self.headerLine, row, 2, 1, 1)
        row += 1
        mainLayout.addWidget(self.contentArea, row, 0, 1, 3)
        self.setLayout(self.mainLayout)

        def start_animation(checked):
            arrow_type = QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow
            direction = (
                QtCore.QAbstractAnimation.Forward
                if checked
                else QtCore.QAbstractAnimation.Backward
            )
            toggleButton.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        # noinspection PyUnresolvedReferences
        self.toggleButton.clicked.connect(start_animation)

    def setContentLayout(self, contentLayout):
        # Not sure if this is equivalent to self.contentArea.destroy()
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = contentLayout.sizeHint().height()
        for i in range(self.toggleAnimation.animationCount()-1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedHeight)
            spoilerAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(
            self.toggleAnimation.animationCount() - 1
        )
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)
