import logging
from .colors import colorize

_stream = None  # In tests can be replaced with io.StringIO to be able to capture to str


class MyLogger:
    def __init__(self) -> None:

        self.formatter = None

        self.datefmt = "%Y-%m-%d %H:%M"
        self.logger = logging.getLogger("application")
        self.logger.addFilter(self.ContextFilter())

    def init_formatter(self, FORMATTER_FILE_STR, FORMATTER_CONSOLE_STR, OUTPUT, LEVEL):
        self.FORMATTER_FILE_STR = FORMATTER_FILE_STR
        self.FORMATTER_CONSOLE_STR = FORMATTER_CONSOLE_STR
        self.OUTPUT = OUTPUT
        self.get_handler()
        self.logger.setLevel(getattr(logging, LEVEL))

    def get_handler(self):
        """If FORMATTER_FILE_STR, FORMATTER_CONSOLE_STR or OUTPUT change, it need new handler.
        First update new value in Mylogger object, then call this function."""
        while self.logger.handlers:
            self.logger.removeHandler(self.logger.handlers[0])
        if self.OUTPUT == "console":
            handler = logging.StreamHandler(stream=_stream)
            self.get_formatter(self.FORMATTER_CONSOLE_STR)
        else:
            handler = logging.FileHandler(self.OUTPUT)
            self.get_formatter(self.FORMATTER_FILE_STR)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def get_formatter(self, format_str):
        self.formatter = logging.Formatter(
            format_str,
            datefmt=self.datefmt,
            style="{",
        )

    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.funcName = "" if record.funcName == "<module>" else f"in function {record.funcName}"
            record.levelname = colorize(record.levelname, record.levelname)
            return True
