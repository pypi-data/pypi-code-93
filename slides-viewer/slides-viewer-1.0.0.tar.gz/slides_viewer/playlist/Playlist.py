from __future__ import annotations

from typing import NewType

from PySide2.QtCore import QUrl

from slides_viewer.playlist.Animation import Animation, AnimationIndex, Animations
from slides_viewer.playlist.Slide import Slide, SlideIndex, Slides

PlaylistIndex = NewType("PlaylistIndex", int)


class Playlist:
    def __init__(self, slides: Slides) -> None:
        self.animationsLength = sum(map(len, slides))
        self.slidesLength = len(slides)

        self.slides = slides

    def getAnimationsLength(self) -> int:
        return self.animationsLength

    def getSlidesLength(self) -> int:
        return self.slidesLength

    def getSlide(self, slideIndex: SlideIndex) -> Slide:
        return self.slides[slideIndex]

    def getIndexOfAnimation(self, slideIndex: SlideIndex, animationIndex: AnimationIndex) -> PlaylistIndex:
        return PlaylistIndex(sum(map(len, self.slides[:slideIndex])) + animationIndex)
