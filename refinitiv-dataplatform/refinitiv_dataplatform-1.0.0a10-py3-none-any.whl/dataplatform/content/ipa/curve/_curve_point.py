# coding: utf8
# contract_gen 2020-06-15 10:07:47.570306

__all__ = ["CurvePoint"]

from ...instrument._definition import ObjectDefinition
from ._instrument import Instrument


class CurvePoint(ObjectDefinition):
    def __init__(
        self,
        start_date=None,
        end_date=None,
        tenor=None,
        instruments=None,
        discount_factor=None,
        rate_percent=None,
    ):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.tenor = tenor
        self.instruments = instruments
        self.discount_factor = discount_factor
        self.rate_percent = rate_percent

    @property
    def instruments(self):
        """
        :return: list Instrument
        """
        return self._get_list_parameter(Instrument, "instruments")

    @instruments.setter
    def instruments(self, value):
        self._set_list_parameter(Instrument, "instruments", value)

    @property
    def discount_factor(self):
        """
        :return: float
        """
        return self._get_parameter("discountFactor")

    @discount_factor.setter
    def discount_factor(self, value):
        self._set_parameter("discountFactor", value)

    @property
    def end_date(self):
        """
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def rate_percent(self):
        """
        :return: float
        """
        return self._get_parameter("ratePercent")

    @rate_percent.setter
    def rate_percent(self, value):
        self._set_parameter("ratePercent", value)

    @property
    def start_date(self):
        """
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def tenor(self):
        """
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)
