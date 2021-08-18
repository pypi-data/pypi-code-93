from enum import Enum
from typing import Dict

import simplejson as json

from .core import ApiClient, BaseClient, ApiClientException, who_am_i
from .env_node import EnvNodes
from .env_settings import EnvSettings


class Status(Enum):
    Running = 1
    Down = 2
    Launching = 3
    Sleep = 4
    Unknown = 5
    Creating = 6
    Cloning = 7
    NotExists = 8
    Exporting = 9
    Migrating = 10
    Broken = 11
    Updating = 12
    Stopping = 13
    GoingToSleep = 14
    Restoring = 15


class ControlClient(BaseClient):
    jelastic_group = "environment"

    jelastic_class = "control"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    def create_environment(self, env: EnvSettings, nodes: EnvNodes) -> str:
        env_json = json.dumps(env)
        nodes_json = json.dumps(nodes)
        response = self.execute(who_am_i(), env=env_json, nodes=nodes_json)
        return response["response"]["env"]["envName"]

    def delete_env(self, env_name: str) -> None:
        self.execute(
            who_am_i(),
            envName=env_name
        )

    def get_env_info(self, env_name: str) -> Dict:
        try:
            response = self.execute(
                who_am_i(),
                envName=env_name
            )
            return response
        except ApiClientException as e:
            return {
                "result": e.response["result"],
                "env": {
                    "status": Status.NotExists
                }
            }

    def env_is_running(self, env_name: str) -> bool:
        env_info = self.get_env_info(env_name)
        env_status = Status(env_info["env"]["status"])

        return env_status == Status.Running

    def env_exists(self, env_name: str) -> bool:
        env_info = self.get_env_info(env_name)
        env_status = Status(env_info["env"]["status"])

        return env_status is not Status.NotExists and env_status is not Status.Unknown
