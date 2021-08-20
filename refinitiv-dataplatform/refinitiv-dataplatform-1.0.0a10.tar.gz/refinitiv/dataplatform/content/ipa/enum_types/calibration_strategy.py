# coding: utf8
# contract_gen 2020-05-18 08:30:59.234842

__all__ = ["CalibrationStrategy"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class CalibrationStrategy(Enum):
    ALL_MATURITY = "AllMaturity"
    DEFAULT = "Default"
    MGB_CALIBRATION = "MGBCalibration"
    MATURITY_BY_MATURITY = "MaturityByMaturity"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(CalibrationStrategy, _CALIBRATION_STRATEGY_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _CALIBRATION_STRATEGY_VALUES_IN_LOWER_BY_CALIBRATION_STRATEGY, some
        )


_CALIBRATION_STRATEGY_VALUES = tuple(t.value for t in CalibrationStrategy)
_CALIBRATION_STRATEGY_VALUES_IN_LOWER_BY_CALIBRATION_STRATEGY = {
    name.lower(): item for name, item in CalibrationStrategy.__members__.items()
}
