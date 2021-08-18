import sys
from typing import Any, Text, NoReturn

import convo.shared.utils.io


def printing_color(*args: Any, color: Text):
    print(convo.shared.utils.io.wrapping_with_color(*args, color=color))


def printing_success(*args: Any):
    printing_color(*args, color=convo.shared.utils.io.bcolours.OK_GREEN)


def printing_information(*args: Any):
    printing_color(*args, color=convo.shared.utils.io.bcolours.OK_BLUE)


def printing_warning(*args: Any):
    printing_color(*args, color=convo.shared.utils.io.bcolours.WARN)


def printing_error(*args: Any):
    printing_color(*args, color=convo.shared.utils.io.bcolours.FAILED)


def printing_error_exit(message: Text, exit_code: int = 1) -> NoReturn:
    """Print error message and exit the application."""

    printing_error(message)
    sys.exit(exit_code)
