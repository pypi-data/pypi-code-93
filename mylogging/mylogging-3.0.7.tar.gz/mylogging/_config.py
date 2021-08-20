"""
This is internal module that has class Config and create and instance config that is imported
in __init__.py, so you will find documentation there...
"""

from typing import List, Union
from pathlib import Path
import re
import logging

from ._helpers import type_and_option_check
from ._logger import MyLogger
from . import colors


class Config:
    """Do not edit class variables, but created instance config in this module...
    All variables has own docstrings.
    """

    def __init__(self):
        self._OUTPUT = "console"
        self._LEVEL = "WARNING"
        self._AROUND = "auto"
        self._used_around = True
        self._COLORIZE = "auto"
        self._FILTER = "once"
        self._FORMATTER_FILE_STR = "{asctime} {levelname} {filename}:{lineno}{message}"
        self._FORMATTER_CONSOLE_STR = "\n{levelname}from {pathname}:{lineno} {funcName}{message}"
        self._BLACKLIST = []
        self._logger = MyLogger()
        self._logger.init_formatter(
            self.FORMATTER_FILE_STR, self.FORMATTER_CONSOLE_STR, self.OUTPUT, self.LEVEL
        )

    # Next variables are used mostly internally, configure only if you know what are you doing
    _console_log_or_warn = (
        "log"  # If log, logging module will trigger to stderr, if "warn", warning will be raised
    )
    _repattern = re.compile(
        r"[\W_]+"
    )  # This is regex that edit logs for filter to be able to use 'once' for example also for tracebacks

    @property
    def FILTER(self) -> str:
        """
        Define what to do with logs, that repeats.

        Only first 100 symbols of message will be used if using once.

        Options: ["ignore", "once", "always", "error"]

        Defaults to: 'once'

        "error" means that application stop on log as on error.
        """
        return self._FILTER

    @FILTER.setter
    def FILTER(self, new):
        type_and_option_check(
            new, options=["ignore", "once", "always", "error"], types=str, variable="FILTER"
        )
        self._FILTER = new

    @property
    def AROUND(self) -> Union[str, bool]:
        """
        True: separate logs with ===== and line breaks for better visibility.

        False: keep message short

        "auto": False if OUTPUT == "file/path", True if OUTPUT == "console"

        Defaults to: "auto"
        """
        return self._AROUND

    @AROUND.setter
    def AROUND(self, new):

        type_and_option_check(new, options=[True, False, "auto"], types=(bool, str), variable="AROUND")
        if new == "auto":
            self._used_around = True if self.OUTPUT == "console" else False
        else:
            self._used_around = new
        self._AROUND = new

    @property
    def FORMATTER_FILE_STR(self) -> str:
        """You can edit used formatter if you want. Just go to source of logging.Formatter to see
        all possible options. This is only main string of formatter class (style="{" is used).
        Message itself is formatted in return_str function. This is for formatter if logging to console.

        Defaults to: "{asctime} {levelname} {filename}:{lineno}{message}"

        """
        return self._FORMATTER_FILE_STR

    @FORMATTER_FILE_STR.setter
    def FORMATTER_FILE_STR(self, new):
        type_and_option_check(new, types=str, variable="FORMATTER_FILE_STR")
        self._FORMATTER_FILE_STR = new
        self._logger.FORMATTER_FILE_STR = new
        self._logger.get_handler(),

    @property
    def FORMATTER_CONSOLE_STR(self) -> str:
        """You can edit used formatter if you want. Just go to source of logging.Formatter to see
        all possible options. This is only main string of formatter class (style="{" is used).
        Message itself is formatted in return_str function. This is for formatter if logging to console.

        Defaults to: "\n{levelname}from {pathname}:{lineno} {funcName}{message}"
        """
        return self._FORMATTER_CONSOLE_STR

    @FORMATTER_CONSOLE_STR.setter
    def FORMATTER_CONSOLE_STR(self, new):
        type_and_option_check(new, types=str, variable="FORMATTER_CONSOLE_STR")
        self._FORMATTER_CONSOLE_STR = new
        self._logger.FORMATTER_CONSOLE_STR = new
        self._logger.get_handler(),

    @property
    def COLORIZE(self) -> Union[str, bool]:
        """Whether colorize results.

        Options: [True, False, 'auto']

        Defaults to: 'auto'

        'auto' means color if to console, not color if to file.
        """
        return self._COLORIZE

    @COLORIZE.setter
    def COLORIZE(self, new):
        type_and_option_check(new, options=(True, False, "auto"), variable="COLORIZE")
        if new == "auto":
            if self.OUTPUT == "console":
                colors.USE_COLORS = True
            else:
                colors.USE_COLORS = False
        else:
            colors.USE_COLORS = new
        self._COLORIZE = new

    @property
    def OUTPUT(self) -> Union[str, Path]:
        """Whether log to file or to console.

        Options: ["console", pathlib.Path, r"path/to/file"]

        Defaults to: "console"
        """
        return self._OUTPUT

    @OUTPUT.setter
    def OUTPUT(self, new):
        type_and_option_check(new, types=(str, Path), variable="OUTPUT")
        self._OUTPUT = new
        self.AROUND = self.AROUND  # If auto, change it
        self.COLORIZE = self.COLORIZE  # If auto, change it
        self._logger.OUTPUT = new
        self._logger.get_handler()

    @property
    def BLACKLIST(self) -> List[str]:
        """Log messages can be filtered out. Only part of message can be used.
        Numeric letters are removed in message comparison, to be able to filter
        out same errors from different places. Only last 100 messages is kept in memory...

        Example: ["Matrix inversion failed"]

        Defaults to: None"""
        return self._BLACKLIST

    @BLACKLIST.setter
    def BLACKLIST(self, new):
        type_and_option_check(new, types=(type(None), list), variable="BLACKLIST")
        self._BLACKLIST = [self._repattern.sub("", i) for i in new]

    @property
    def LEVEL(self) -> str:
        """Logs can be filtered out based on log severity.

        Options: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        Defaults to: "INFO"

        Also WARN and FATAL can be used, but will be converted to WARNING and CRITICAL.
        """
        return self._LEVEL

    @LEVEL.setter
    def LEVEL(self, new):
        new = new.upper()

        type_and_option_check(
            new, types=(str), options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], variable="LEVEL"
        )
        if new == "FATAL":
            new = "CRITICAL"

        if new == "WARN":
            new = "WARNING"

        if self.OUTPUT:
            self._logger.logger.setLevel(getattr(logging, new))
        self._LEVEL = new


config = Config()
