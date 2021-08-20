# coding: utf8
# contract_gen 2020-05-19 11:24:17.162470

__all__ = ["BasketItem"]

from ..instrument._definition import ObjectDefinition


class BasketItem(ObjectDefinition):
    def __init__(self, instrument_code=None, currency=None):
        super().__init__()
        self.instrument_code = instrument_code
        self.currency = currency

    @property
    def currency(self):
        """
        :return: str
        """
        return self._get_parameter("currency")

    @currency.setter
    def currency(self, value):
        self._set_parameter("currency", value)

    @property
    def instrument_code(self):
        """
        Data Type: string
        Code to define the Reverse Convertible instrument.It can be an ISIN, a RIC or an AssetId.
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)
