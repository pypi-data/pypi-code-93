import logging
from logging import Logger
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler
from typing import Dict

from ctlml_commons.log.gzip_rotator import GZipRotator
from ctlml_commons.util.constants import ACCESS_LOG_NAME
from ctlml_commons.util.io_utils import ensure_exists

LOGGERS: Dict[str, Logger] = {}


def create_logger(a_path: str) -> Logger:
    """
    Creates a rotating log
    """

    ensure_exists(a_path)

    log_name: str = a_path.split("/")[-1]

    if log_name in LOGGERS:
        return LOGGERS[log_name]

    logger = logging.getLogger(log_name.split(".")[0])
    logger.setLevel(logging.INFO)

    log_handler = TimedRotatingFileHandler(filename=a_path, when="h")

    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)
    log_handler.rotator = GZipRotator()

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(log_formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(log_handler)

    LOGGERS[log_name] = logger

    return logger


def init_logging(log_dir: str, app_type: str):
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s:%(funcName)s: %(message)s",
                    "datefmt": "%d/%b/%Y:%H:%M:%S",
                },
                "access": {"format": "%(message)s"},
            },
            "loggers": {
                "": {"level": "INFO", "handlers": ["default", "stream"], "propagate": True},
                ACCESS_LOG_NAME: {
                    "level": "INFO",
                    "handlers": ["access_logs"],
                    "propagate": False,
                },
                "root": {"level": "INFO", "handlers": ["default"]},
            },
            "handlers": {
                "stream": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "default": {
                    "level": "INFO",
                    "class": "ctlml_commons.log.GzipTimedRotatingFileHandler",
                    "filename": f"{log_dir}/{app_type}_api.log",
                    "formatter": "default",
                    "delay": True,
                },
                "access_logs": {
                    "level": "INFO",
                    "class": "ctlml_commons.log.GzipTimedRotatingFileHandler",
                    "filename": f"{log_dir}/{app_type}_access.log",
                    "formatter": "access",
                    "delay": True,
                },
            },
        }
    )
