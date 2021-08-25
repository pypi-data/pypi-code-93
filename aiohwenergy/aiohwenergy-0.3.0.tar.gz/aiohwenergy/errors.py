"""Aiohwenergy errors."""


class AiohwenergyException(Exception):
    """Base error for aiohwenergy."""


class RequestError(AiohwenergyException):
    """Unable to fulfill request.

    Raised when host or API cannot be reached.
    """


class InvalidStateError(AiohwenergyException):
    """Raised when the device is not in the correct state."""


class UnsupportedError(AiohwenergyException):
    """Raised when the device is not supported from this library."""


class DisabledError(AiohwenergyException):
    """Raised when device API is disabled. User has to enable API in app."""


ERRORS = {
    1: RequestError,
    2: InvalidStateError,
    3: UnsupportedError,
    101: DisabledError,
}


def raise_error(code, message):
    """Raise error based on error type."""
    cls = ERRORS.get(code, AiohwenergyException)
    raise cls("{}: {}".format(code, message))
