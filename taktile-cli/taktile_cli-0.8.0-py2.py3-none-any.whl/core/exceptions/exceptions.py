import http
from typing import List

from pydantic import ValidationError


class TklException(Exception):
    ...


class MissingDocker(Exception):
    ...


class NotInitializedError(Exception):
    ...


class VersionError(Exception):
    ...


class CLIError(Exception):
    ...


class ModelNotFoundError(Exception):
    ...


class EndpointException(Exception):
    ...


class ConversionException(EndpointException):
    ...


class ValidationException(EndpointException):
    ...


class ProjectValidationException(TklException):
    ...


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str = None) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class APISwitchException(Exception):
    # TODO: Remove this in taktile-cli 1.0
    pass


class APIClientException(HTTPException):
    ...

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class APIClientExceptionRetryable(APIClientException):
    ...


class UserRepoValidationException(ProjectValidationException):
    def __init__(
        self, missing_files: List, missing_directories: List, missing_config: bool
    ):
        self.missing_files = missing_files
        self.missing_directories = missing_directories
        self.missing_config = missing_config


class NoContentsFoundException(UserRepoValidationException):
    ...


class TktlConfigInvalidException(ProjectValidationException):
    def __init__(self, validation_error: ValidationError):
        self.err = validation_error


def validate_config(fn):
    from tktl.core.managers.project import ProjectManager

    def wrapper(*args, **kwargs):
        if ProjectManager.get_config() is None:
            raise CLIError(
                "No configuration found. Are you sure you have a tktl.yaml file in "
                "your current directory? Run tktl init to start a new project"
            )
        return fn(*args, **kwargs)

    return wrapper
