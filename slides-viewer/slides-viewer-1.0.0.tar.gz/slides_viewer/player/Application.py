from typing import Sequence, cast

from PySide2.QtCore import Qt, SignalInstance
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QApplication

from slides_viewer.player.Player import Player
from slides_viewer.player.Window import Window
from slides_viewer.playlist.Playlist import Playlist


class Application(QApplication):
    def __init__(self, playlist: Playlist, argv: Sequence[str]) -> None:
        super().__init__(argv)

        self.setApplicationName("Slides Viewer")

        self.window = Window(self.desktop())
        cast(SignalInstance, self.window.keyPress).connect(self._keyPressEvent)

        self.player = Player(self.window.getViewer(), playlist)

        self.window.show()

    def _keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:
            self.player.playPause()

        if event.key() == Qt.Key_Left:
            self.player.prev()

        if event.key() == Qt.Key_Right:
            self.player.next()

        if event.key() == Qt.Key_F:
            self.window.toggleFullscreen()
