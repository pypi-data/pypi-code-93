from enum import Enum


class Status(str, Enum):
    """Resulting status of some action."""

    success = "success"
    failure = "failure"
    error = "error"
