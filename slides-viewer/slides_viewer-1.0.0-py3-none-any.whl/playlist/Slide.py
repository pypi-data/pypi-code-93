from enum import Enum
from typing import NewType, Sequence

from slides_viewer.playlist.Animation import Animations

SlideIndex = NewType("SlideIndex", int)


class Slide:
    class SlideType(Enum):
        SEQUENCE = 1
        LOOP = 2

    def __init__(self, animations: Animations, slideType: SlideType) -> None:
        self.animations = animations
        self.length = len(animations)
        self.slideType = slideType

    def __len__(self) -> int:
        return self.length

    def getAnimations(self) -> Animations:
        return self.animations

    def getType(self) -> SlideType:
        return self.slideType


Slides = Sequence[Slide]
