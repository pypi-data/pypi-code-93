# coding: utf8
# contract_gen 2020-05-19 11:24:17.151933

__all__ = ["InterpolationWeight"]

from ..instrument._definition import ObjectDefinition
from ..models import DayWeight


class InterpolationWeight(ObjectDefinition):
    def __init__(self, days_list=None, holidays=None, week_days=None, week_ends=None):
        super().__init__()
        self.days_list = days_list
        self.holidays = holidays
        self.week_days = week_days
        self.week_ends = week_ends

    @property
    def days_list(self):
        """
        :return: list DayWeight
        """
        return self._get_list_parameter(DayWeight, "daysList")

    @days_list.setter
    def days_list(self, value):
        self._set_list_parameter(DayWeight, "daysList", value)

    @property
    def holidays(self):
        """
        :return: float
        """
        return self._get_parameter("holidays")

    @holidays.setter
    def holidays(self, value):
        self._set_parameter("holidays", value)

    @property
    def week_days(self):
        """
        :return: float
        """
        return self._get_parameter("weekDays")

    @week_days.setter
    def week_days(self, value):
        self._set_parameter("weekDays", value)

    @property
    def week_ends(self):
        """
        :return: float
        """
        return self._get_parameter("weekEnds")

    @week_ends.setter
    def week_ends(self, value):
        self._set_parameter("weekEnds", value)
