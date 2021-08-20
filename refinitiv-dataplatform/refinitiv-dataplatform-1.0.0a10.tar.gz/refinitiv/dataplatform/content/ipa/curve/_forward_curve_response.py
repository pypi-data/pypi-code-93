# coding: utf8
# contract_gen 2020-06-15 10:07:47.566307

__all__ = ["ForwardCurveResponse"]

from ..instrument._definition import ObjectDefinition
from .forward import ForwardCurveResponseItem


class ForwardCurveResponse(ObjectDefinition):
    def __init__(self, data=None):
        super().__init__()
        self.data = data

    @property
    def data(self):
        """
        :return: list ForwardCurveResponseItem
        """
        return self._get_list_parameter(ForwardCurveResponseItem, "data")

    @data.setter
    def data(self, value):
        self._set_list_parameter(ForwardCurveResponseItem, "data", value)
