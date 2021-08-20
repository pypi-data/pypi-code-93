# coding: utf8
# contract_gen 2020-05-18 08:30:59.200816

__all__ = ["AmortizationFrequency"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class AmortizationFrequency(Enum):
    EVERY12TH_COUPON = "Every12thCoupon"
    EVERY2ND_COUPON = "Every2ndCoupon"
    EVERY3RD_COUPON = "Every3rdCoupon"
    EVERY4TH_COUPON = "Every4thCoupon"
    EVERY_COUPON = "EveryCoupon"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            AmortizationFrequency, _AMORTIZATION_FREQUENCY_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _AMORTIZATION_FREQUENCY_VALUES_IN_LOWER_BY_AMORTIZATION_FREQUENCY, some
        )


_AMORTIZATION_FREQUENCY_VALUES = tuple(t.value for t in AmortizationFrequency)
_AMORTIZATION_FREQUENCY_VALUES_IN_LOWER_BY_AMORTIZATION_FREQUENCY = {
    name.lower(): item for name, item in AmortizationFrequency.__members__.items()
}
