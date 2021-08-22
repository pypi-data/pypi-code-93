from typing import NewType, Sequence

from PySide2.QtCore import QUrl

AnimationIndex = NewType("AnimationIndex", int)


class Animation:
    def __init__(self, path: QUrl) -> None:
        self.path = path

    def getPath(self) -> QUrl:
        return self.path


Animations = Sequence[Animation]
