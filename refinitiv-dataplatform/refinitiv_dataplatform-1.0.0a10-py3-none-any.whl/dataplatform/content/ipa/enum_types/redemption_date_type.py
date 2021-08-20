# coding: utf8
# contract_gen 2020-05-18 08:30:59.210816

__all__ = ["RedemptionDateType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class RedemptionDateType(Enum):
    REDEMPTION_AT_AVERAGE_LIFE = "RedemptionAtAverageLife"
    REDEMPTION_AT_BEST_DATE = "RedemptionAtBestDate"
    REDEMPTION_AT_CALL_DATE = "RedemptionAtCallDate"
    REDEMPTION_AT_CUSTOM_DATE = "RedemptionAtCustomDate"
    REDEMPTION_AT_MAKE_WHOLE_CALL_DATE = "RedemptionAtMakeWholeCallDate"
    REDEMPTION_AT_MATURITY_DATE = "RedemptionAtMaturityDate"
    REDEMPTION_AT_NEXT_DATE = "RedemptionAtNextDate"
    REDEMPTION_AT_PAR_DATE = "RedemptionAtParDate"
    REDEMPTION_AT_PARTIAL_CALL_DATE = "RedemptionAtPartialCallDate"
    REDEMPTION_AT_PARTIAL_PUT_DATE = "RedemptionAtPartialPutDate"
    REDEMPTION_AT_PERPETUITY = "RedemptionAtPerpetuity"
    REDEMPTION_AT_PREMIUM_DATE = "RedemptionAtPremiumDate"
    REDEMPTION_AT_PUT_DATE = "RedemptionAtPutDate"
    REDEMPTION_AT_SINK_DATE = "RedemptionAtSinkDate"
    REDEMPTION_AT_WORST_DATE = "RedemptionAtWorstDate"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(RedemptionDateType, _REDEMPTION_DATE_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _REDEMPTION_DATE_TYPE_VALUES_IN_LOWER_BY_REDEMPTION_DATE_TYPE, some
        )


_REDEMPTION_DATE_TYPE_VALUES = tuple(t.value for t in RedemptionDateType)
_REDEMPTION_DATE_TYPE_VALUES_IN_LOWER_BY_REDEMPTION_DATE_TYPE = {
    name.lower(): item for name, item in RedemptionDateType.__members__.items()
}
