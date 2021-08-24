import inspect

from .api_client import ApiClient
from .base_client import BaseClient
from .exceptions import ApiClientException, JelasticClientException


def who_am_i() -> str:
    function_name_in_snake_case = inspect.stack()[1][3]
    return "".join(function_name_in_snake_case.split('_'))
