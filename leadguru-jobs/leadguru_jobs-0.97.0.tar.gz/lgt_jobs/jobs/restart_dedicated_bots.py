from abc import ABC

from lgt_data.mongo_repository import DedicatedBotRepository, UserMongoRepository
from pydantic import BaseModel

from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob
from ..env import k8namespace, backend_uri, project_id, aggregator_topic, google_app_credentials

"""
Restart Bots
"""
class RestartDedicatedBotsJobData(BaseBackgroundJobData, BaseModel):
    user_id: str

class RestartDedicatedBotsJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return RestartDedicatedBotsJobData

    def exec(self, data: RestartDedicatedBotsJobData):
        from ..k8client import KubernetesClientFactory

        user = UserMongoRepository().get(data.user_id)
        deployment_name = user.email \
            .replace("@", "-") \
            .replace(".", "-") \
            .replace(".", "-") \
            .replace("#", "-") \
            .replace("+", "-")

        deployment_labels = {"type": f"dedicated-bots-{deployment_name}"}

        client = KubernetesClientFactory.create()
        client.remove_deployments(k8namespace, deployment_labels)
        bots = DedicatedBotRepository().get_user_bots(data.user_id)

        if not bots:
            return

        response = client.create_slack_bots_deployment(namespace=k8namespace,
                                                       name=f"dedicated-bots-{deployment_name}",
                                                       backend_uri=backend_uri,
                                                       bots=bots,
                                                       project_id=project_id,
                                                       aggregator_topic=aggregator_topic,
                                                       google_app_credentials=google_app_credentials,
                                                       labels=deployment_labels)