import logging
import os
from typing import Optional, cast

import colorama
from pythonjsonlogger import jsonlogger

from . import colorful
from .context import ContextLogger
from .level import SUCCESS

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


def patch() -> None:
    if logging.getLoggerClass() == ContextLogger:
        return

    os.environ["PYCHARM_HOSTED"] = "true"
    colorama.init()

    logging.addLevelName(SUCCESS, "SUCCESS")
    logging.setLoggerClass(ContextLogger)

    logger = logging.getLogger()
    logger.setLevel(logging.getLevelName(os.environ.get("LOGLEVEL", "INFO").upper()))
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(levelname)s %(filename) %(lineno)s %(message)s",
        json_serializer=colorful.dumps,
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


def getLogger(name: Optional[str] = None) -> ContextLogger:
    patch()
    return cast(ContextLogger, logging.getLogger(name))
