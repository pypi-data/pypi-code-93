from abc import ABC, abstractmethod

from .api_client import ApiClient
from .exceptions import JelasticClientException


def success_response(response: dict) -> bool:
    return response["result"] == 0


class BaseClient(ABC):

    def __init__(self, api_client: ApiClient):
        self._api_client = api_client

    @property
    @abstractmethod
    def jelastic_group(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def jelastic_class(self):
        raise NotImplementedError

    def _execute(self, fnc: str, **kwargs) -> dict:
        two_dotted_function_name = self._fnc(fnc)
        response = self._api_client.execute(
            two_dotted_function_name,
            **kwargs
        )

        if not success_response(response):
            raise JelasticClientException(
                f"execution of function {two_dotted_function_name} failed", response)

        return response

    def _fnc(self, fnc_name: str):
        return f"{self.jelastic_group}.{self.jelastic_class}.{fnc_name}"
