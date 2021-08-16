"""
CoaClient commands exceptions
"""

from coaclient.exceptions.base import CoaClientBaseException

__all__ = (
    "CoaClientCommandException",
)


class CoaClientCommandException(CoaClientBaseException):
    """ coaclient exception class for custom exception """
    _STR = "CoaClient command exception: {message}"
