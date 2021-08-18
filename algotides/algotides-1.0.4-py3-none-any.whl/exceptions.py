"""
This file will contain all exceptions used in the rest of this project.
"""

# Python
from pathlib import Path


class TidesException(Exception):
    pass


class TidesBadEncoding(TidesException):
    """
    Used when de-serializing some jsonpickle file that does not correspond to the expected object.
    """
    def __init__(self, path: Path, expected: type, actual: type):
        super().__init__(f"{path} serialized file was not the object type it was supposed to be:\n"
                         f"Expected type:\t\t{expected}\n"
                         f"De-serialized type:\t{actual}")


class TidesBadTransactionField(TidesException):
    """
    Used when gathering content from TransactionWindow fields that is invalid.
    """
    def __init__(self, field: str, reason: str):
        super().__init__(f"Field \"{field}\" of the transaction was invalid.\n"
                         f"Reason: {reason}")


class TidesInvalidWidgetState(TidesException):
    """
    Used when a method for a Tides custom widget is called and the widget is in a state where the request
    can't be interpreted.
    """
    def __init__(self, message: str):
        super().__init__(message)
