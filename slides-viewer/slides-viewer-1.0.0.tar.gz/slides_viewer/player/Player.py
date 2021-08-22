from enum import Enum
from logging import error, info
from typing import List, Optional, cast

from PySide2.QtCore import SignalInstance
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtWidgets import QStackedWidget

from slides_viewer.player.AnimationVideo import AnimationVideo
from slides_viewer.playlist.Animation import AnimationIndex
from slides_viewer.playlist.Playlist import Playlist, PlaylistIndex
from slides_viewer.playlist.Slide import Slide, SlideIndex


class Player:
    class FollowingAction(Enum):
        NOTHING = 0
        NEXT = 1
        PREV = 2
        WAITING = 3

    def __init__(self, viewer: QStackedWidget, playlist: Playlist) -> None:
        super().__init__()

        self.playlistWidgets: List[Optional[AnimationVideo]] = [None] * playlist.getAnimationsLength()
        self.playlistIndex: PlaylistIndex = PlaylistIndex(0)
        self.slideIndex: SlideIndex = SlideIndex(0)

        self.viewer = viewer
        self.playlist = playlist

        self.followingAction = Player.FollowingAction.NOTHING

        self._preloadSlide(SlideIndex(0))
        self._preloadSlide(SlideIndex(1))
        self._playAnimation()

    def next(self) -> None:
        if not self.slideIndex < self.playlist.getSlidesLength() - 1:
            return None

        if self.followingAction != Player.FollowingAction.WAITING:
            if self.followingAction != Player.FollowingAction.NEXT:
                self.followingAction = Player.FollowingAction.NEXT
                return None

        self._unloadSlide(SlideIndex(self.slideIndex - 1))

        self.followingAction = Player.FollowingAction.NOTHING

        self.slideIndex = SlideIndex(self.slideIndex + 1)
        self._playAnimation()

        self._preloadSlide(SlideIndex(self.slideIndex + 1))

    def prev(self) -> None:
        if not self.slideIndex > 0:
            return None

        if self.followingAction != Player.FollowingAction.WAITING:
            if self.followingAction != Player.FollowingAction.PREV:
                self.followingAction = Player.FollowingAction.PREV
                return None

        self._unloadSlide(SlideIndex(self.slideIndex + 1))

        self.followingAction = Player.FollowingAction.NOTHING

        self.slideIndex = SlideIndex(self.slideIndex - 1)
        self._playAnimation()

        self._preloadSlide(SlideIndex(self.slideIndex - 1))

    def playPause(self) -> None:
        if len(self.playlistWidgets) == 0:
            return error("There is nothing to play")

        videoWidget = self.playlistWidgets[self.playlistIndex]

        if videoWidget is None:
            return None

        mediaPlayer = videoWidget.getMediaPlayer()

        if mediaPlayer.state() == QMediaPlayer.State.PlayingState:
            mediaPlayer.pause()
        elif mediaPlayer.state() == QMediaPlayer.State.PausedState:
            mediaPlayer.play()
        else:
            self._playAnimation()

    def _preloadSlide(self, slideIndex: SlideIndex) -> None:
        if not 0 <= slideIndex < self.playlist.getSlidesLength():
            return None

        info(f"Preloading slide {slideIndex}:")

        slide = self.playlist.getSlide(slideIndex)
        offsetIndex = self.playlist.getIndexOfAnimation(slideIndex, AnimationIndex(0))

        for playlistIndex, animation in enumerate(slide.getAnimations(), start=offsetIndex):
            if self.playlistWidgets[playlistIndex] is not None:
                continue

            animationIndex = AnimationIndex(playlistIndex - offsetIndex)
            videoWidget = AnimationVideo(animation, slideIndex, animationIndex)

            info(f'> Preloading animation {animationIndex}: "{videoWidget.getAnimationFileName()}"')

            self.playlistWidgets[playlistIndex] = videoWidget
            cast(SignalInstance, videoWidget.animationFinished).connect(self._endOfAnimation)
            self.viewer.addWidget(videoWidget)

    def _unloadSlide(self, slideIndex: SlideIndex) -> None:
        if not 0 <= slideIndex < self.playlist.getSlidesLength():
            return None

        info(f"Unloading slide {slideIndex}:")

        offsetIndex = self.playlist.getIndexOfAnimation(slideIndex, AnimationIndex(0))
        animationsLength = len(self.playlist.getSlide(slideIndex))

        for playlistIndex in range(offsetIndex, offsetIndex + animationsLength):
            animationIndex = AnimationIndex(playlistIndex - offsetIndex)
            videoWidget = self.playlistWidgets[playlistIndex]

            if videoWidget is None:
                continue

            info(f'> Unloading animation {animationIndex}: "{videoWidget.getAnimationFileName()}"')

            self.viewer.removeWidget(videoWidget)
            cast(SignalInstance, videoWidget.animationFinished).disconnect()
            self.playlistWidgets[playlistIndex] = None

    def _playAnimation(self, animationIndex: AnimationIndex = AnimationIndex(0)) -> None:
        if not 0 <= animationIndex < self.playlist.getAnimationsLength():
            return None

        videoIndex = self.playlist.getIndexOfAnimation(self.slideIndex, animationIndex)
        videoWidget = self.playlistWidgets[videoIndex]

        if videoWidget is None:
            return None

        info(f'Playing "{videoWidget.getAnimationFileName()}" (slide: {self.slideIndex}, animation: {animationIndex})')

        mediaPlayer = videoWidget.getMediaPlayer()

        mediaPlayer.pause()
        mediaPlayer.setPosition(0)

        currentWidget = self.viewer.currentWidget()

        if isinstance(currentWidget, AnimationVideo):
            currentWidget.getMediaPlayer().pause()

        self.viewer.setCurrentWidget(videoWidget)
        mediaPlayer.play()

        self.playlistIndex = videoIndex

    def _endOfAnimation(self, slideIndex: SlideIndex, animationIndex: AnimationIndex) -> None:
        slide = self.playlist.getSlide(slideIndex)

        if animationIndex < len(slide) - 1:
            return self._playAnimation(AnimationIndex(animationIndex + 1))

        if self.followingAction == Player.FollowingAction.NEXT:
            return self.next()
        elif self.followingAction == Player.FollowingAction.PREV:
            return self.prev()

        if slide.getType() == Slide.SlideType.LOOP:
            return self._playAnimation()

        self.followingAction = Player.FollowingAction.WAITING
