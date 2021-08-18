from abc import ABC, abstractmethod
from typing import Dict

from .api_client import ApiClient
from .exceptions import JelasticClientException


def success_response(response: Dict) -> bool:
    return response["result"] == 0


class BaseClient(ABC):

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    @property
    @abstractmethod
    def jelastic_group(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def jelastic_class(self):
        raise NotImplementedError

    def execute(self, fnc: str, **kwargs) -> Dict:
        two_dotted_function_name = self._fnc(fnc)
        response = self.api_client.execute(
            two_dotted_function_name,
            **kwargs
        )

        if not success_response(response):
            raise JelasticClientException(
                f"execution of function {two_dotted_function_name} failed", response)

        return response

    def _fnc(self, fnc_name: str):
        return f"{self.jelastic_group}.{self.jelastic_class}.{fnc_name}"
