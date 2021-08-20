# coding: utf8
# contract_gen 2020-05-18 08:30:59.207816

__all__ = ["StubRule"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class StubRule(Enum):
    ISSUE = "Issue"
    LONG_FIRST_FULL = "LongFirstFull"
    MATURITY = "Maturity"
    SHORT_FIRST_FULL = "ShortFirstFull"
    SHORT_FIRST_PRO_RATA = "ShortFirstProRata"
    SHORT_LAST_PRO_RATA = "ShortLastProRata"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(StubRule, _STUB_RULE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_STUB_RULE_VALUES_IN_LOWER_BY_STUB_RULE, some)


_STUB_RULE_VALUES = tuple(t.value for t in StubRule)
_STUB_RULE_VALUES_IN_LOWER_BY_STUB_RULE = {
    name.lower(): item for name, item in StubRule.__members__.items()
}
