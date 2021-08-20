from jelastic_client.core import BaseClient, ApiClient, who_am_i


class FileClient(BaseClient):
    jelastic_group = "environment"

    jelastic_class = "file"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    def read(self, env_name: str, path: str, node_type: str = None, node_group: str = None, node_id: str = None) -> str:
        response = self._execute(
            who_am_i(),
            envName=env_name,
            path=path,
            nodeType=node_type,
            nodeGroup=node_group,
            nodeid=node_id
        )
        return response["body"]
