from typing import cast

from PySide2.QtCore import Qt, Signal, SignalInstance
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QDesktopWidget, QMainWindow, QStackedWidget


class Window(QMainWindow):
    keyPress = Signal(QKeyEvent)

    def __init__(self, desktop: QDesktopWidget) -> None:
        super().__init__()

        self.setStyleSheet("background-color: black;")

        self.viewer = QStackedWidget()
        self.setCentralWidget(self.viewer)

        screenRect = desktop.screenGeometry(1)
        self.move(screenRect.x(), screenRect.y())

        self.viewer.setMinimumSize(854, 480)
        self.viewer.setMaximumSize(4096, 2160)

    def getViewer(self) -> QStackedWidget:
        return self.viewer

    def keyPressEvent(self, event: QKeyEvent) -> None:
        cast(SignalInstance, self.keyPress).emit(event)

    def toggleFullscreen(self) -> None:
        if self.windowState() & Qt.WindowFullScreen:
            self.setWindowState(Qt.WindowActive)
        else:
            self.setWindowState(Qt.WindowFullScreen)
