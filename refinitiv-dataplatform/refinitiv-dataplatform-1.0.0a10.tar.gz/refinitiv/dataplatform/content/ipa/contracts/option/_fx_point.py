# coding: utf8
# contract_gen 2020-06-03 11:34:39.518949

__all__ = ["FxPoint"]

from ...instrument._definition import ObjectDefinition
from ...enum_types.status import Status


class FxPoint(ObjectDefinition):
    def __init__(
        self,
        bid=None,
        ask=None,
        mid=None,
        status=None,
        instrument=None,
        processing_information=None,
        spot_decimals=None,
    ):
        super().__init__()
        self.bid = bid
        self.ask = ask
        self.mid = mid
        self.status = status
        self.instrument = instrument
        self.processing_information = processing_information
        self.spot_decimals = spot_decimals

    @property
    def status(self):
        """
        :return: enum Status
        """
        return self._get_enum_parameter(Status, "status")

    @status.setter
    def status(self, value):
        self._set_enum_parameter(Status, "status", value)

    @property
    def ask(self):
        """
        :return: float
        """
        return self._get_parameter("ask")

    @ask.setter
    def ask(self, value):
        self._set_parameter("ask", value)

    @property
    def bid(self):
        """
        :return: float
        """
        return self._get_parameter("bid")

    @bid.setter
    def bid(self, value):
        self._set_parameter("bid", value)

    @property
    def instrument(self):
        """
        :return: str
        """
        return self._get_parameter("instrument")

    @instrument.setter
    def instrument(self, value):
        self._set_parameter("instrument", value)

    @property
    def mid(self):
        """
        :return: float
        """
        return self._get_parameter("mid")

    @mid.setter
    def mid(self, value):
        self._set_parameter("mid", value)

    @property
    def processing_information(self):
        """
        :return: str
        """
        return self._get_parameter("processingInformation")

    @processing_information.setter
    def processing_information(self, value):
        self._set_parameter("processingInformation", value)

    @property
    def spot_decimals(self):
        """
        :return: str
        """
        return self._get_parameter("spotDecimals")

    @spot_decimals.setter
    def spot_decimals(self, value):
        self._set_parameter("spotDecimals", value)
