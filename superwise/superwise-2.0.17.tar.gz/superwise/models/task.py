""" This module implement Task model  """
from superwise.models.base import BaseModel


class Task(BaseModel):
    """ Task model class, model  for tasks data """

    def __init__(
        self,
        id=None,
        external_id=None,
        title=None,
        task_description=None,
        task_type=None,
        monitor_delay=None,
        time_units=None,
        is_archive=None,
        **kwargs
    ):
        """
        constructer for Version class

        :param external_id:
        :param task_id:
        :param title:
        :param task_description:
        :param task_type_id:
        :param label:
        :param allow_label_overwrite:
        :param allow_prediction_update:
        :param ongoing_label:
        :param fictive_label_mapper:
        :param monitor_delay:
        :param time_units:
        """
        self.external_id = external_id
        self.title = title
        self.id = id or None
        self.task_description = task_description
        self.task_type = self.get_enum_value(task_type)
        self.monitor_delay = monitor_delay
        self.time_units = time_units
        self.is_archive = is_archive
