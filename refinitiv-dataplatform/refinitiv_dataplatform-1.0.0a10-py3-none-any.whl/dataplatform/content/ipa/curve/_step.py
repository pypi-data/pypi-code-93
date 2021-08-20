# coding: utf8
# contract_gen 2020-06-15 10:07:47.563306

__all__ = ["Step"]

from ..instrument._definition import ObjectDefinition


class Step(ObjectDefinition):
    def __init__(self, date=None, rate_percent=None):
        super().__init__()
        self.date = date
        self.rate_percent = rate_percent

    @property
    def date(self):
        """
        EffectiveDate: effective date of the rate step
        :return: str
        """
        return self._get_parameter("date")

    @date.setter
    def date(self, value):
        self._set_parameter("date", value)

    @property
    def rate_percent(self):
        """
        RatePercent: stepped rate expressed in percent
        :return: float
        """
        return self._get_parameter("ratePercent")

    @rate_percent.setter
    def rate_percent(self, value):
        self._set_parameter("ratePercent", value)
