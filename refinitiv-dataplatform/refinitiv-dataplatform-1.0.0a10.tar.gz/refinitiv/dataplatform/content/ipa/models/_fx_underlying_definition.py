# coding: utf8
# contract_gen 2020-05-19 11:24:17.150215

__all__ = ["FxUnderlyingDefinition"]

from ..instrument._definition import ObjectDefinition


class FxUnderlyingDefinition(ObjectDefinition):
    def __init__(self, fx_cross_code=None):
        super().__init__()
        self.fx_cross_code = fx_cross_code

    @property
    def fx_cross_code(self):
        """
        The currency pair.
        Should contain the two currencies, ex EURUSD
        :return: str
        """
        return self._get_parameter("fxCrossCode")

    @fx_cross_code.setter
    def fx_cross_code(self, value):
        self._set_parameter("fxCrossCode", value)
