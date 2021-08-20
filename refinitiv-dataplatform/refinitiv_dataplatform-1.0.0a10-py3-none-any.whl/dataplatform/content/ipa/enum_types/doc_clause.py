# coding: utf8
# contract_gen 2020-05-13 12:48:48.744016

__all__ = ["DocClause"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class DocClause(Enum):
    CUM_RESTRUCT14 = "CumRestruct14"
    MODIFIED_RESTRUCT14 = "ModifiedRestruct14"
    MOD_MOD_RESTRUCT14 = "ModModRestruct14"
    EX_RESTRUCT14 = "ExRestruct14"
    CUM_RESTRUCT03 = "CumRestruct03"
    MODIFIED_RESTRUCT03 = "ModifiedRestruct03"
    MOD_MOD_RESTRUCT03 = "ModModRestruct03"
    EX_RESTRUCT03 = "ExRestruct03"
    NONE = "None"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(DocClause, _DOC_CLAUSE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_DOC_CLAUSE_VALUES_IN_LOWER_BY_DOC_CLAUSE, some)


_DOC_CLAUSE_VALUES = tuple(t.value for t in DocClause)
_DOC_CLAUSE_VALUES_IN_LOWER_BY_DOC_CLAUSE = {
    name.lower(): item for name, item in DocClause.__members__.items()
}
