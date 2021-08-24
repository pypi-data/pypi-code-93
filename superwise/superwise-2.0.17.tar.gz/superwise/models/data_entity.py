""" This module implement DataEntity model  """
import json

import pandas as pd

from superwise.models.base import BaseModel


class DataEntity(BaseModel):
    """ data entity model class """

    def __init__(
        self,
        id=None,
        dimension_start_ts=None,
        type=None,
        name=None,
        role=None,
        feature_importance=None,
        summary=None,
        secondary_type=None,
        **kwargs
    ):
        """
        constructer for DataEntity class

        :param type:
        :param name:
        :param is_dimension:
        :param role:
        :param feature_importance:
        """
        self.name = name.lower() if name else None
        self.type = self.get_enum_value(type)
        self.role = self.get_enum_value(role)
        self.feature_importance = feature_importance
        self.summary = summary
        self.secondary_type = secondary_type
        self.id = id
        self.dimension_start_ts = self.from_datetime(dimension_start_ts)

    @staticmethod
    def list_to_df(data_entities):
        data = [d.get_properties() for d in data_entities]
        df = pd.DataFrame(data)
        return df

    @staticmethod
    def df_to_list(data_entities_df):
        data = json.loads(data_entities_df.to_json(orient="records"))
        entities = []
        [entities.append(DataEntity(**d)) for d in data]
        return entities


class DataEntityCollection:
    def __init__(self, entities=None, reuse_previus_entities=False):
        self.reuse_previus_entities = reuse_previus_entities
        self.entities = entities or []

    def add_entity(self, entity):
        self.entities.append(entity)


class DataEntitySummary(BaseModel):
    """ summary model class """

    def __init__(self, idx=None, summary=None):
        """
        constructer for DataEntitySummary class

        :param idx:
        :param summary:
        """
        self.id = idx
        self.summary = summary
