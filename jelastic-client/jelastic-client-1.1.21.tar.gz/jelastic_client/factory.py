from .file_client import FileClient
from .control_client import ControlClient
from .core import ApiClient
from .jps_client import JpsClient


class JelasticClientFactory:
    def __init__(self, api_url: str, api_token: str):
        self.api_client = ApiClient(api_url, api_token)

    def create_jps_client(self) -> JpsClient:
        return JpsClient(self.api_client)

    def create_control_client(self) -> ControlClient:
        return ControlClient(self.api_client)

    def create_file_client(self) -> FileClient:
        return FileClient(self.api_client)
