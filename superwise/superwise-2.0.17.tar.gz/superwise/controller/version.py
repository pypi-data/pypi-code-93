""" This module implement version functionality  """
import time

from superwise.config import Config
from superwise.controller.base import BaseController
from superwise.controller.exceptions import SuperwiseValidationException
from superwise.models.data_entity import DataEntity


class VersionController(BaseController):
    """ Version api controller """

    def __init__(self, client, sw):
        """
        Constructor of VersionController

        :param client: rest api client
        """
        super().__init__(client, sw)
        self.path = "model/v1/versions"
        self.model_name = "Version"

    def create(self, model, is_return_model=True, base_version=None, wait_until_complete=False, **kwargs):
        """

        :param model: model of version
        :return: model of version
        """
        entities_with_summary = None
        task = self.sw.task.get_by_id(model.task_id)
        if model.baseline_df is not None:

            entities_with_summary = self.sw.data_entity.generate_summary(
                model.data_entities, task, model.baseline_df, base_version=base_version
            )

            model.baseline_df = None
            model.data_entities = entities_with_summary
        if len(model.data_entities) and isinstance(model.data_entities[0], DataEntity):
            model.data_entities = [m.get_properties() for m in model.data_entities]
        res = super().create(model, **kwargs)
        if wait_until_complete:
            return self.get_by_id(res.id, wait_until_complete)
        else:
            return res

    def _dict(self, params, model_name=None):
        """

        :param params: dict
        :return: model of version
        """
        model_name = model_name or self.model_name

        model = super()._dict_to_model(params, model_name=model_name)

        if model_name != "DataEntity" and len(model.data_entities) and isinstance(model.data_entities[0], DataEntity):
            model.data_entities = [m.get_properties() for m in model.data_entities]
        return model

    def get_data_entities(self, version_id):
        """

        :param version_id:
        :return: list of models of data entities
        """
        models = []
        url = self.build_url("{}/{}/data_entities".format(self.path, version_id))
        self.logger.info("CALL GET DATA ENTITIES {} ".format(url))
        r = self.client.get(url)
        entities_lst = self.parse_response(r, "DataEntity", is_return_model=False)
        entities_lst = [e["data_entity"] for e in entities_lst]
        for entity in entities_lst:
            models.append(self._dict_to_model(entity, "DataEntity"))
        return models

    def get_by_id(self, idx, wait_until_complete=False):
        """ get by id implementation as we need to implement pooling version"""
        if wait_until_complete:
            while True:
                time.sleep(Config.POOLING_INTERVAL_SEC)
                model = super().get_by_id(idx)
                status = model.status
                if status in ["CREATED"]:
                    self.logger.info(
                        "job status: CREATED, summerizing should start soon, next pooling in %s sec",
                        Config.POOLING_INTERVAL_SEC,
                    )
                elif status in ["SUMMARIZING"]:
                    self.logger.info("still summerizing the data, next pooling in %s sec", Config.POOLING_INTERVAL_SEC)
                    continue
                elif status == "SUMMARIZED":
                    self.logger.info("finished summerizing the version, return results")
                    return model
                elif status in ["VALIDATION_ERROR"]:
                    raise SuperwiseValidationException(model.get_properties())
                else:
                    raise Exception("unknown status %s", model.get_properties())
        else:
            return super().get_by_id(idx)

    def activate(self, version_id):
        url = "{}/{}".format(self.path, version_id)
        res = self.patch(url, {"status": "ACTIVATED"})
        return res
