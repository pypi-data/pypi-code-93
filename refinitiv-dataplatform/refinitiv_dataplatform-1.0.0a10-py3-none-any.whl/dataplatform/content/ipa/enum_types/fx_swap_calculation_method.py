# coding: utf8
# contract_gen 2020-05-18 08:30:59.226816

__all__ = ["FxSwapCalculationMethod"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class FxSwapCalculationMethod(Enum):
    DEPOSIT_CCY1_IMPLIED_FROM_FX_SWAP = "DepositCcy1ImpliedFromFxSwap"
    DEPOSIT_CCY2_IMPLIED_FROM_FX_SWAP = "DepositCcy2ImpliedFromFxSwap"
    FX_SWAP = "FxSwap"
    FX_SWAP_IMPLIED_FROM_DEPOSIT = "FxSwapImpliedFromDeposit"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            FxSwapCalculationMethod, _FX_SWAP_CALCULATION_METHOD_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _FX_SWAP_CALCULATION_METHOD_VALUES_IN_LOWER_BY_FX_SWAP_CALCULATION_METHOD,
            some,
        )


_FX_SWAP_CALCULATION_METHOD_VALUES = tuple(t.value for t in FxSwapCalculationMethod)
_FX_SWAP_CALCULATION_METHOD_VALUES_IN_LOWER_BY_FX_SWAP_CALCULATION_METHOD = {
    name.lower(): item for name, item in FxSwapCalculationMethod.__members__.items()
}
