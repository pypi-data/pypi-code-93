# coding: utf8
# contract_gen 2020-06-03 11:34:39.450949

__all__ = ["Status"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class Status(Enum):
    NOT_APPLICABLE = "NotApplicable"
    USER = "User"
    DATA = "Data"
    COMPUTED = "Computed"
    ERROR = "Error"
    NONE = "None"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Status, _STATUS_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_STATUS_VALUES_IN_LOWER_BY_STATUS, some)


_STATUS_VALUES = tuple(t.value for t in Status)
_STATUS_VALUES_IN_LOWER_BY_STATUS = {
    name.lower(): item for name, item in Status.__members__.items()
}
