"""
Calculation of the transient climate response (TCR)
"""
from .base import _CalculatorTCRTCREBase
from .utils import _time_mean


class CalculatorTCR(_CalculatorTCRTCREBase):
    """
    Calculator of the transient climate response (TCR)
    """

    @classmethod
    def _can_calculate_metric(cls, metric):
        return metric == "Transient Climate Response"

    @classmethod
    def _calculate(
        cls, assessed_ranges, res_calc, norm_period, evaluation_period, unit
    ):
        res_calc_normed = cls._get_normed_res_calc(
            assessed_ranges, res_calc, norm_period, evaluation_period
        )

        out = _time_mean(
            res_calc_normed.filter(
                scenario="1pctCO2",
                variable="Surface Air Temperature Change",
                unit=unit,
                region="World",
                year=1920,
            )
        )

        return out
