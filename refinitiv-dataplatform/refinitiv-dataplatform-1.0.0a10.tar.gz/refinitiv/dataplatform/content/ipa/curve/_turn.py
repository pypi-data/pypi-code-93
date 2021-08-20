# coding: utf8
# contract_gen 2020-06-15 10:07:47.564306

__all__ = ["Turn"]

from ..instrument._definition import ObjectDefinition


class Turn(ObjectDefinition):
    def __init__(self, month=None, rate_percent=None, year=None):
        super().__init__()
        self.month = month
        self.rate_percent = rate_percent
        self.year = year

    @property
    def month(self):
        """
        Month of the turn period
        :return: int
        """
        return self._get_parameter("month")

    @month.setter
    def month(self, value):
        self._set_parameter("month", value)

    @property
    def rate_percent(self):
        """
        Turn rate expressed in percents
        :return: float
        """
        return self._get_parameter("ratePercent")

    @rate_percent.setter
    def rate_percent(self, value):
        self._set_parameter("ratePercent", value)

    @property
    def year(self):
        """
        Year of the turn period
        :return: int
        """
        return self._get_parameter("year")

    @year.setter
    def year(self, value):
        self._set_parameter("year", value)
