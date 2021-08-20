# coding: utf8
# contract_gen 2020-06-03 11:34:39.541923

__all__ = ["PayoutScaling"]

from ..instrument._definition import ObjectDefinition


class PayoutScaling(ObjectDefinition):
    def __init__(self, maximum=None, minimum=None):
        super().__init__()
        self.maximum = maximum
        self.minimum = minimum

    @property
    def maximum(self):
        """
        :return: float
        """
        return self._get_parameter("maximum")

    @maximum.setter
    def maximum(self, value):
        self._set_parameter("maximum", value)

    @property
    def minimum(self):
        """
        :return: float
        """
        return self._get_parameter("minimum")

    @minimum.setter
    def minimum(self, value):
        self._set_parameter("minimum", value)
