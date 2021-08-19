# -*- coding: utf-8 -*-
import sys
from typing import Any


class XuelangCloudException:
    
    def __init__(self, code=None, message=None, requestId=None):
        self.code = code
        self.message = message
        self.requestId = requestId

    def __str__(self):
        s = "[XuelangCloudException] code:%s message:%s requestId:%s" % (
            self.code, self.message, self.requestId)
        if sys.version_info[0] < 3 and isinstance(s, str):
            return s.encode("utf8")
        else:
            return s

    def get_code(self):
        return self.code

    def get_message(self):
        return self.message

    def get_request_id(self):
        return self.requestId


# Exceptions encountered while interection with the Hub backend
class AuthenticationException(Exception):
    def __init__(self, message="Authentication failed. Please try logging in again."):
        super().__init__(message)


class AuthorizationException(Exception):
    def __init__(
        self,
        message="You are not authorized to access this resource on Activeloop Server.",
    ):
        super().__init__(message)


class InvalidPasswordException(AuthorizationException):
    def __init__(
        self,
        message="The password you provided was invalid.",
    ):
        super().__init__(message)


class CouldNotCreateNewDatasetException(AuthorizationException):
    def __init__(
        self,
        path: str,
    ):

        extra = ""
        if path.startswith("hub://"):
            extra = "Since the path is a `hub://` dataset, if you believe you should have write permissions, try running `activeloop login`."

        message = f"Dataset at '{path}' doesn't exist, and you have no permissions to create one there. Maybe a typo? {extra}"
        super().__init__(message)


class ResourceNotFoundException(Exception):
    def __init__(
        self,
        message="The resource you are looking for was not found. Check if the name or id is correct.",
    ):
        super().__init__(message)


class BadRequestException(Exception):
    def __init__(self, message):
        message = (
            f"Invalid Request. One or more request parameters is incorrect.\n{message}"
        )
        super().__init__(message)


class OverLimitException(Exception):
    def __init__(
        self,
        message="You are over the allowed limits for this operation.",
    ):
        super().__init__(message)


class ServerException(Exception):
    def __init__(self, message="Internal Activeloop server error."):
        super().__init__(message)


class BadGatewayException(Exception):
    def __init__(self, message="Invalid response from Activeloop server."):
        super().__init__(message)


class GatewayTimeoutException(Exception):
    def __init__(self, message="Activeloop server took too long to respond."):
        super().__init__(message)


class WaitTimeoutException(Exception):
    def __init__(self, message="Timeout waiting for server state update."):
        super().__init__(message)


class LockedException(Exception):
    def __init__(self, message="The resource is currently locked."):
        super().__init__(message)


class UnexpectedStatusCodeException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidTokenException(Exception):
    def __init__(self, message="The authentication token is empty or error."):
        super().__init__(message)


class ProjectNotFound(Exception):
    def __init__(self, message="Project is not found."):
        super().__init__(message)


class PropertyDoesNotExistError(KeyError):
    def __init__(self, property_name: str):
        super().__init__(f"Property '{property_name}' does not exist.")


class InvalidKeyTypeError(TypeError):
    def __init__(self, item: Any):
        super().__init__(
            f"Item '{str(item)}' of type '{type(item).__name__}' is not a valid key."
        )
