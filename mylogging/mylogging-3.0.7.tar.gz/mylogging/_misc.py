"""
This module is internal module for mylogging library. It's not supposed to be used by user.
"""

# from datetime import datetime
import warnings

from ._config import config
from . import colors


printed_infos = set()
user_filters = []
original_formatwarning = warnings.formatwarning
level_str_to_int = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


logging_functions = {
    "DEBUG": config._logger.logger.debug,
    "INFO": config._logger.logger.info,
    "WARNING": config._logger.logger.warning,
    "ERROR": config._logger.logger.error,
    "CRITICAL": config._logger.logger.critical,
}


class CustomWarning(UserWarning):
    pass


def filter_out(message, level):
    # All logging can be turned off
    if config.FILTER == "ignore":
        return True

    # Check if sufficient level

    if level_str_to_int[level] < level_str_to_int[config.LEVEL]:
        return True

    message = config._repattern.sub("", message)[:150]

    # Filters
    if config.FILTER == "once":
        if message in printed_infos:
            return True
        else:
            printed_infos.add(message)

    for i in config.BLACKLIST:
        if i in message:
            return True


def log_warn(message, level, showwarning_details=True, stack_level=3):
    """If _TO_FILE is configured, it will log message into file on path _TO_FILE. If not _TO_FILE is configured, it will
    warn or print INFO message.

    Args:
        message (str): Any string content of warning.
        log_type (str): 'INFO' or something else, generated automatically from __init__ module.
        edit_showwarning (bool): Whether to override warnings details display. After warning, default one will be again used.
            Defaults to True.
    """

    if config.FILTER == "error":
        raise RuntimeError(message)

    if config._console_log_or_warn == "log":
        try:
            # From version 3.8
            logging_functions[level](message, stacklevel=stack_level)
        except TypeError:
            logging_functions[level](message)

    else:
        warnings.formatwarning = formatwarning_detailed if showwarning_details else formatwarning_stripped

        CustomWarning.__name__ = level
        CustomWarning.level = level

        warnings.warn(message, stacklevel=stack_level, category=CustomWarning)

        warnings.formatwarning = original_formatwarning


def objectize_str(message):
    """Make a class from a string to be able to apply escape characters and colors if raise.

    Args:
        message (str): Any string you use.

    Returns:
        Object: Object, that can return string if printed or used in warning or raise.
    """

    class X(str):
        def __repr__(self):
            return f"{message}"

    return X(message)


def formatwarning_detailed(message, category, filename, lineno, *args, **kwargs):
    """Function that can override warnings printed info. """
    return f"\n\n{colors.colorize(category.__name__, level=category.level, use=config.COLORIZE)}from {filename}:{lineno} {message}\n"


def formatwarning_stripped(message, *args, **kwargs):
    """Function that can override warnings printed info."""
    return f"{message}\n"
