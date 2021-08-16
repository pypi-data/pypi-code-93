"""
CoaClient base exception
"""
__all__ = (
    "CoaClientBaseException",
)


class CoaClientBaseException(Exception):
    """ Base exception class for custom exception """
    _STR = None

    def __init__(self, message: str, *args):
        self.message = message
        super().__init__(message, *args)

    def __str__(self):
        if self._STR is None:
            return super().__str__()
        return self._STR.format(
            message=self.message
        )
