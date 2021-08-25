import json

from http import HTTPStatus

from quick_client import ApiException
from quick_client import ErrorMessage


class NotInitializedException(Exception):
    def __init__(
        self,
        message="Not initialized.\nPlease run:\n\t$ quick init\nto set your host and API key.",
    ):
        self.message = message
        super().__init__(self.message)


class HostNotSetException(Exception):
    def __init__(
        self,
        message="Host not set.\nPlease run:\n\t$ quick init\nto set your host and API key.",
    ):
        self.message = message
        super().__init__(self.message)


class InvalidApiKeyException(Exception):
    def __init__(self, message="Unauthorized.\n Your API key is invalid."):
        self.message = message
        super().__init__(self.message)


class InvalidNameException(Exception):
    def __init__(
        self,
        message="Invalid name.\n Use only lowercase alphanumeric characters (no more than 253 characters). '-', or '.' are allowed.",
    ):
        self.message = message
        super().__init__(self.message)


class ManagerException(Exception):
    def __init__(self, message="The quick manager returned an error."):
        self.message = message
        super().__init__(self.message)


class ConfigException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def handle_error(exception: ApiException, message: str = None):
    status_code = exception.status
    json_body = json.loads(exception.body)
    error_message = ErrorMessage(
        json_body["type"],
        json_body["title"],
        json_body["code"],
        json_body["detail"],
        json_body["uriPath"],
    )

    if status_code == HTTPStatus.UNAUTHORIZED:
        raise InvalidApiKeyException
    else:
        if message is not None:
            msg = f"{error_message.title}: {error_message.detail}\n{message}"
        else:
            msg = f"{error_message.title}: {error_message.detail}"
        raise ManagerException(msg)
