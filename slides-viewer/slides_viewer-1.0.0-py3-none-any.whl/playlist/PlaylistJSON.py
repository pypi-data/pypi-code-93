from json import load
from logging import error
from pathlib import Path
from typing import Literal, Optional

from jsonschema import validate  # type: ignore
from jsonschema.exceptions import ValidationError  # type: ignore
from PySide2.QtCore import QUrl

from slides_viewer.playlist.Animation import Animation, AnimationIndex, Animations
from slides_viewer.playlist.Playlist import Playlist
from slides_viewer.playlist.Slide import Slide, SlideIndex, Slides

schema = {
    "type": "object",
    "properties": {
        "files": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "end_animation": {"type": "number", "minimum": 0},
                    "start_animation": {"type": "number", "minimum": 0},
                    "number": {"type": "number", "minimum": 1},
                    "type": {"type": "string", "oneOf": [{"enum": ["slide", "loop"]}]},
                },
                "required": ["end_animation", "start_animation", "number", "type"],
            },
            "minItems": 1,
        },
    },
    "required": ["files", "slides"],
}


class PlaylistJSON:
    SlideType = Literal["slide", "loop"]

    @staticmethod
    def readFromFile(path: Path) -> Optional[Playlist]:
        with open(path) as jsonFile:
            try:
                json = load(jsonFile)
            except ValueError as err:
                error(f"Unable to read JSON file {path}: {err}")
                return None

        try:
            validate(json, schema)
        except ValidationError as err:
            error(f"Unable to read JSON file {path}: {err}")
            return None

        animations: Animations = list(map(lambda file: Animation(QUrl(file)), json["files"]))
        slides: Slides = list(map(lambda slide: PlaylistJSON._createSlide(animations, **slide), json["slides"]))

        return Playlist(slides)

    @staticmethod
    def _createSlide(
        animations: Animations, start_animation: AnimationIndex, end_animation: AnimationIndex, type: SlideType, number: SlideIndex
    ) -> Slide:
        if type == "slide":
            slideType = Slide.SlideType.SEQUENCE
        elif type == "loop":
            slideType = Slide.SlideType.LOOP

        return Slide(animations[start_animation:end_animation], slideType)
