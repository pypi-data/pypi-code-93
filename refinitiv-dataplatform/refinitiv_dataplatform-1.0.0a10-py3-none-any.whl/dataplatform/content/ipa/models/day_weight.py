# coding: utf8
# contract_gen 2020-05-19 11:24:17.152933

__all__ = ["DayWeight"]

from ..instrument._definition import ObjectDefinition


class DayWeight(ObjectDefinition):
    def __init__(self, date=None, weight=None):
        super().__init__()
        self.date = date
        self.weight = weight

    @property
    def date(self):
        """
        :return: str
        """
        return self._get_parameter("date")

    @date.setter
    def date(self, value):
        self._set_parameter("date", value)

    @property
    def weight(self):
        """
        :return: float
        """
        return self._get_parameter("weight")

    @weight.setter
    def weight(self, value):
        self._set_parameter("weight", value)
