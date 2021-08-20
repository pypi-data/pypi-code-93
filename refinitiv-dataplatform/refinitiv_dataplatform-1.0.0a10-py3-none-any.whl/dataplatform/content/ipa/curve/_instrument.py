# coding: utf8
# contract_gen 2020-06-15 10:07:47.571306

__all__ = ["Instrument"]

from ...instrument._definition import ObjectDefinition


class Instrument(ObjectDefinition):
    def __init__(self, instrument_code=None, value=None):
        super().__init__()
        self.instrument_code = instrument_code
        self.value = value

    @property
    def instrument_code(self):
        """
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def value(self):
        """
        :return: float
        """
        return self._get_parameter("value")

    @value.setter
    def value(self, value):
        self._set_parameter("value", value)
