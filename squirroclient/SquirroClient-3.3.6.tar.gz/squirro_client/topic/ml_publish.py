import json
import logging

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLPublishMixin(object):

    #
    #  ML Publish
    #
    def get_ml_published_models(self, project_id):
        """Returns all the publishing model for a given project.

        :param project_id: Id of the Squirro project.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)["pub_items"]

    def get_ml_published_model(self, project_id, publish_id):
        """Returns the details of the a published model.

        :param project_id: Id of the Squirro project.
        :param publish_id: id of the published model.
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish/%(publish_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "publish_id": publish_id,
            }
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def ml_publish_model(self, project_id, model_id, published_as, description):
        """Publish new ML Model.

        :param project_id: Id of the Squirro project.
        :param model_id: ID of the model to be published.
        :param published_as: Name of the published model.
        :param description: Text to be shown describing the model.
        """

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        publish_model_params = {
            "model_id": model_id,
            "published_as": published_as,
            "description": description,
            "token": self.refresh_token,
        }

        res = self._perform_request(
            "post", url, data=json.dumps(publish_model_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_published_model(
        self, project_id, publish_id, model_id, published_as, description
    ):
        """Update ML Published model

        :param project_id: Id of the Squirro project.
        :param publish_id: id of the published model
        :param model_id: ID of the model to be published.
        :param published_as: Name of the published model.
        :param description: Text to be shown describing the model.
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish/%(publish_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "publish_id": publish_id,
            }
        )
        headers = {"Content-Type": "application/json"}

        model_params = {
            "model_id": model_id,
            "published_as": published_as,
            "description": description,
            "token": self.refresh_token,
        }
        res = self._perform_request(
            "put", url, data=json.dumps(model_params), headers=headers
        )
        return self._process_response(res, [204])

    def unpublish_ml_model(self, project_id, publish_id):
        """Delete ML Model

        :param project_id: Id of the Squirro project.
        :param publish_id: Id of the  published Model.
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish/%(publish_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "publish_id": publish_id,
            }
        )

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])
