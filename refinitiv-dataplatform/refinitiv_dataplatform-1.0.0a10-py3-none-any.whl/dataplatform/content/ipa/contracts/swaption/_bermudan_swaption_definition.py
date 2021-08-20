# coding: utf8
# contract_gen 2020-06-03 11:34:39.569937

__all__ = ["BermudanSwaptionDefinition"]

from ...enum_types.exercise_schedule_type import ExerciseScheduleType
from ...instrument._definition import ObjectDefinition


class BermudanSwaptionDefinition(ObjectDefinition):
    def __init__(
        self,
        exercise_schedule=None,
        exercise_schedule_type=None,
        notification_days=None,
    ):
        super().__init__()
        self.exercise_schedule = exercise_schedule
        self.exercise_schedule_type = exercise_schedule_type
        self.notification_days = notification_days

    @property
    def exercise_schedule(self):
        """
        Overridable exercise schedule
        :return: list string
        """
        return self._get_list_parameter(str, "exerciseSchedule")

    @exercise_schedule.setter
    def exercise_schedule(self, value):
        self._set_list_parameter(str, "exerciseSchedule", value)

    @property
    def exercise_schedule_type(self):
        """
        :return: enum ExerciseScheduleType
        """
        return self._get_enum_parameter(ExerciseScheduleType, "exerciseScheduleType")

    @exercise_schedule_type.setter
    def exercise_schedule_type(self, value):
        self._set_enum_parameter(ExerciseScheduleType, "exerciseScheduleType", value)

    @property
    def notification_days(self):
        """
        :return: int
        """
        return self._get_parameter("notificationDays")

    @notification_days.setter
    def notification_days(self, value):
        self._set_parameter("notificationDays", value)
