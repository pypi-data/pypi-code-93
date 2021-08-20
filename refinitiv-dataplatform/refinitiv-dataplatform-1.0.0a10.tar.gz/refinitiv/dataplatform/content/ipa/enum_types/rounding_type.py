# coding: utf8
# contract_gen 2020-05-18 08:30:59.212840

__all__ = ["RoundingType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class RoundingType(Enum):
    CEIL = "Ceil"
    DEFAULT = "Default"
    DOWN = "Down"
    FACE_DOWN = "FaceDown"
    FACE_NEAR = "FaceNear"
    FACE_UP = "FaceUp"
    FLOOR = "Floor"
    NEAR = "Near"
    UP = "Up"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(RoundingType, _ROUNDING_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_ROUNDING_TYPE_VALUES_IN_LOWER_BY_ROUNDING_TYPE, some)


_ROUNDING_TYPE_VALUES = tuple(t.value for t in RoundingType)
_ROUNDING_TYPE_VALUES_IN_LOWER_BY_ROUNDING_TYPE = {
    name.lower(): item for name, item in RoundingType.__members__.items()
}
