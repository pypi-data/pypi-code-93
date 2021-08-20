# coding: utf8
# contract_gen 2020-05-18 08:30:59.223836

__all__ = ["ExerciseStyle"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class ExerciseStyle(Enum):
    AMER = "AMER"
    BERM = "BERM"
    EURO = "EURO"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(ExerciseStyle, _EXERCISE_STYLE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_EXERCISE_STYLE_VALUES_IN_LOWER_BY_EXERCISE_STYLE, some)


_EXERCISE_STYLE_VALUES = tuple(t.value for t in ExerciseStyle)
_EXERCISE_STYLE_VALUES_IN_LOWER_BY_EXERCISE_STYLE = {
    name.lower(): item for name, item in ExerciseStyle.__members__.items()
}
