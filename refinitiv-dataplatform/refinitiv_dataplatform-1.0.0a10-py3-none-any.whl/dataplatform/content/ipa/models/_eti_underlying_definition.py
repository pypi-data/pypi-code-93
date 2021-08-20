# coding: utf8
# contract_gen 2020-05-19 11:24:17.137187

__all__ = ["EtiUnderlyingDefinition"]

from ..instrument._definition import ObjectDefinition


class EtiUnderlyingDefinition(ObjectDefinition):
    def __init__(self, instrument_code=None):
        super().__init__()
        self.instrument_code = instrument_code

    @property
    def instrument_code(self):
        """
        The underlier RIC
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)
