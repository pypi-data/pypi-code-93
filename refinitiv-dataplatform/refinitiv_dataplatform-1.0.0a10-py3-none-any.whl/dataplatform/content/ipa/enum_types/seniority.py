# coding: utf8
# contract_gen 2020-05-13 12:48:48.744016

__all__ = ["Seniority"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class Seniority(Enum):
    SECURED = "Secured"
    SENIOR_UNSECURED = "SeniorUnsecured"
    SUBORDINATED = "Subordinated"
    JUNIOR_SUBORDINATED = "JuniorSubordinated"
    PREFERENCE = "Preference"
    NONE = "None"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Seniority, _SENIORITY_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_SENIORITY_VALUES_IN_LOWER_BY_SENIORITY, some)


_SENIORITY_VALUES = tuple(t.value for t in Seniority)
_SENIORITY_VALUES_IN_LOWER_BY_SENIORITY = {
    name.lower(): item for name, item in Seniority.__members__.items()
}
