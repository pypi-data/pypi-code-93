from abc import ABC
from typing import Optional

from lgt.common.python.lgt_logging import log
from lgt_data.mongo_repository import BotMongoRepository
from pydantic import BaseModel, conlist

from ..env import k8namespace, backend_uri, project_id, aggregator_topic, google_app_credentials
from ..basejobs import BaseBackgroundJob, BaseBackgroundJobData

"""
Restart Bots
"""
class RestartBotsJobData(BaseBackgroundJobData, BaseModel):
    bots: conlist(str, min_items = 0)
    chunk_size: Optional[int] = 30

class RestartBotsJob(BaseBackgroundJob, ABC):
    @staticmethod
    def _chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    @property
    def job_data_type(self) -> type:
        return RestartBotsJobData

    def exec(self, data: RestartBotsJobData):
        from ..k8client import KubernetesClientFactory

        deployment_labels = { "type": "slack-bot" }
        client = KubernetesClientFactory.create()
        client.remove_deployments(k8namespace, deployment_labels)
        repo = BotMongoRepository()
        bots = repo.get()

        chunk_list = RestartBotsJob._chunks([bot for bot in bots if not bot.invalid_creds], data.chunk_size)
        index = 0

        for chunk in chunk_list:
            name = f'lgt-bots-{index}'
            response = client.create_slack_bots_deployment(namespace=k8namespace,
                                                name=name,
                                                backend_uri=backend_uri,
                                                bots=chunk,
                                                project_id=project_id,
                                                aggregator_topic=aggregator_topic,
                                                google_app_credentials=google_app_credentials,
                                                labels=deployment_labels)

            log.info(f'Deployment {index} has been updated. Response {response}')
            index = index + 1