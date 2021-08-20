# coding: utf8
# contract_gen 2020-06-03 11:34:39.571948

__all__ = ["SwaptionMarketDataRule"]

from ...instrument._definition import ObjectDefinition


class SwaptionMarketDataRule(ObjectDefinition):
    def __init__(self, discount=None, forward=None):
        super().__init__()
        self.discount = discount
        self.forward = forward

    @property
    def discount(self):
        """
        :return: str
        """
        return self._get_parameter("discount")

    @discount.setter
    def discount(self, value):
        self._set_parameter("discount", value)

    @property
    def forward(self):
        """
        :return: str
        """
        return self._get_parameter("forward")

    @forward.setter
    def forward(self, value):
        self._set_parameter("forward", value)
