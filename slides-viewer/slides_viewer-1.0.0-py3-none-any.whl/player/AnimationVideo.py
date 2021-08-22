from logging import error
from typing import cast

from PySide2.QtCore import Signal, SignalInstance
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtMultimediaWidgets import QVideoWidget

from slides_viewer.playlist.Animation import Animation, AnimationIndex
from slides_viewer.playlist.Slide import SlideIndex


class AnimationVideo(QVideoWidget):
    animationFinished = Signal(object, object)

    def __init__(self, animation: Animation, slideIndex: SlideIndex, animationIndex: AnimationIndex) -> None:
        super().__init__()

        self.animationFileName = animation.getPath().fileName()
        self.animationIndex = animationIndex
        self.slideIndex = slideIndex

        self.mediaPlayer = QMediaPlayer(self, cast(QMediaPlayer.Flags, QMediaPlayer.Flag.VideoSurface))
        self.mediaPlayer.setVideoOutput(self)
        self.mediaPlayer.setMedia(animation.getPath())

        self.mediaPlayer.mediaStatusChanged.connect(self.mediaStatusChanged)

    def getMediaPlayer(self) -> QMediaPlayer:
        return self.mediaPlayer

    def getAnimationFileName(self) -> str:
        return self.animationFileName

    def mediaStatusChanged(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            error(f'Unable to play "{self.animationFileName}" (slide: {self.slideIndex}, animation: {self.animationIndex})')
            cast(SignalInstance, self.animationFinished).emit(self.slideIndex, self.animationIndex)

        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            cast(SignalInstance, self.animationFinished).emit(self.slideIndex, self.animationIndex)
