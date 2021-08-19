class MessageableException(Exception):
    """Base class for user related errors."""

    message: str


class MissingPositional(MessageableException):
    """Raised when user forgets to pass positional."""

    def __init__(self, positional, position):
        """

        :param ezcli.Positional positional:
        :param int position:
        """
        self.positional = positional
        self.position: int = position
        self.message = f'Missing {position + 1}. argument!'


class UnexceptedNumberOfValues(MessageableException):
    """Raised when user passes to many or not enough arguments.
    Require ``only_positionals = True`` in a ``Command`` class"""

    def __init__(self, values, expected_len):
        """

        :param list[str] values:
        :param int expected_len:
        """
        self.message = f'Unexcepted number of values, {len(values)} instead of {expected_len}'
