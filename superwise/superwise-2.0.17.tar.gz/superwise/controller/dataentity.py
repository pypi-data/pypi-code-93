""" This module implement data entities functionality  """
import pandas as pd

from superwise.config import Config
from superwise.controller.base import BaseController
from superwise.controller.exceptions import SuperwiseValidationException
from superwise.controller.summary.entities_validator import EntitiesValidator
from superwise.controller.summary.feature_importance import FeatureImportance
from superwise.controller.summary.summary import Summary
from superwise.models.data_entity import DataEntity
from superwise.models.data_entity import DataEntitySummary
from superwise.resources.superwise_enums import CategoricalSecondaryType
from superwise.resources.superwise_enums import FeatureType


class DataEntityController(BaseController):
    """ controller for Data entities  """

    def __init__(self, client, sw):
        """
        constructer for DataEntityController class

        :param client:

        """
        super().__init__(client, sw)
        self.path = "model/v1/data_entities"
        self.model_name = "DataEntity"
        self._entities_df = None
        self.data = None

    @staticmethod
    def _pre_process_data(data):
        data.columns = data.columns.str.lower()
        for column in Config.LIST_DROP_DATA_COLS:
            if column in data.columns:
                data = data.drop(column, axis=1)
        return data

    def create(self, name=None, type=None, dimension_start_ts=None, role=None, feature_importance=None):
        """
        create data entity
        """

        params = locals()
        return self._dict_to_model(params)

    def update_summary(self, data_entity_id, summary):
        """
        update summary implementation
        """
        self.model = DataEntitySummary(data_entity_id, summary)
        self.model_name = "DataEntitySummary"
        self.create(self.model)

    def generate_summary(self, data_entities, task, data, base_version=None, is_return_model=True, **kwargs):
        """
        :param model: model of version
        :return: model of version
        """
        self.data = self._pre_process_data(data)
        # if base_version supplied -> use it: save only new entities
        if base_version:
            if base_version.status not in ["SUMMARIZED", "ACTIVATED"]:
                raise SuperwiseValidationException(
                    "base version should be used for summarized only version, current status: {}".format(
                        base_version.status
                    )
                )
            r = self.client.get(self.build_url("model/v1/versions/{}/data_entities".format(base_version.id)))

            previus_entities = self.parse_response(r, is_return_model=False)
            previus_entities = [e["data_entity"] for e in previus_entities]
            previus_entities_dict = {}
            if previus_entities:
                for data_entity in previus_entities:
                    previus_entities_dict[data_entity["name"]] = data_entity["id"]
            for de in data_entities:
                if de.name in previus_entities_dict:
                    de.id = previus_entities_dict[de.name]
                else:
                    de.id = None
        entities_df = DataEntity.list_to_df(data_entities)
        self._entities_df = entities_df
        validator = EntitiesValidator(task, entities_df, self.data)
        self.data = validator.prepare()
        fi = FeatureImportance(self._entities_df)
        self._entities_df = fi.compute(self.data)
        entities_df_summary = Summary(self._entities_df, self.data).generate()
        data_entities = DataEntity.df_to_list(entities_df_summary)
        return data_entities
