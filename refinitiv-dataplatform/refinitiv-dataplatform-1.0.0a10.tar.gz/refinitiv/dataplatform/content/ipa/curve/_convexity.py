# coding: utf8
# contract_gen 2020-06-15 10:07:47.562310

__all__ = ["ConvexityAdjustment"]

from ..instrument._definition import ObjectDefinition


class ConvexityAdjustment(ObjectDefinition):
    def __init__(self, mean_reversion_percent=None, volatility_percent=None):
        super().__init__()
        self.mean_reversion_percent = mean_reversion_percent
        self.volatility_percent = volatility_percent

    @property
    def mean_reversion_percent(self):
        """
        Reversion speed rate, expressed in percents, used to calculate the convexity adjustment
        :return: float
        """
        return self._get_parameter("meanReversionPercent")

    @mean_reversion_percent.setter
    def mean_reversion_percent(self, value):
        self._set_parameter("meanReversionPercent", value)

    @property
    def volatility_percent(self):
        """
        Reversion flat volatility, expressed in percents, used to calculate the convexity adjustment
        :return: float
        """
        return self._get_parameter("volatilityPercent")

    @volatility_percent.setter
    def volatility_percent(self, value):
        self._set_parameter("volatilityPercent", value)
