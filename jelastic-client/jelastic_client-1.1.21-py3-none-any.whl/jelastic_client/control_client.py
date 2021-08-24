import simplejson as json

from .core import (
    ApiClient,
    BaseClient,
    ApiClientException,
    who_am_i
)
from .env_info import EnvInfo
from .env_settings import EnvSettings
from .env_status import EnvStatus
from .node_settings import MultipleNodeSettings


class ControlClient(BaseClient):
    jelastic_group = "environment"

    jelastic_class = "control"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    def create_environment(self, env: EnvSettings, nodes: MultipleNodeSettings) -> EnvInfo:
        env_json = json.dumps(env)
        nodes_json = json.dumps(nodes)
        response = self._execute(who_am_i(), env=env_json, nodes=nodes_json)
        return EnvInfo(response["response"])

    def delete_env(self, env_name: str) -> None:
        self._execute(
            who_am_i(),
            envName=env_name
        )

    def get_env_info(self, env_name: str) -> EnvInfo:
        try:
            response = self._execute(
                who_am_i(),
                envName=env_name
            )
        except ApiClientException as e:
            response = {
                "result": e.response["result"],
                "env": {
                    "status": EnvStatus.NotExists
                }
            }
        return EnvInfo(response)
