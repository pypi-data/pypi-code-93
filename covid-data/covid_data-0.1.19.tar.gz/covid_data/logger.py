# encoding: utf-8
import logging
import sys


def init_logger(level: int = logging.DEBUG):
    """Initialize the root logger and standard log handlers."""
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    root_logger = logging.getLogger("covid_data")
    root_logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    sys.excepthook = log_uncaught_exception


def log_uncaught_exception(type, value, traceback):
    root_logger = logging.getLogger("covid_data")
    root_logger.exception(f"Uncaught exception: {value}")
