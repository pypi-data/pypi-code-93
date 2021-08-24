""" This module implement version  model  """
import pandas as pd

from superwise.models.base import BaseModel


class Version(BaseModel):
    """ Version model class, model  for version data """

    def __init__(
        self,
        id=None,
        task_id=None,
        version_name=None,
        external_id=None,
        training_ts=None,
        baseline_files=None,
        data_entities=None,
        baseline_df=None,
        status=None,
        **kwargs
    ):
        """
        constructer for Version class

        :param task_id:
        :param version_name:
        :param client_name:
        :param external_id:
        :param trainin_ts:
        :param baseline_files:
        :param data_entities:
        """
        self.id = id
        self.task_id = task_id
        self.version_name = version_name
        self.external_id = external_id
        self.training_ts = training_ts
        self.data_entities = data_entities or []
        self.baseline_files = baseline_files or []
        self.status = status
        self.baseline_df = baseline_df
