import sys
import logging
from sylo.definitions import SYLO_HOME

logger = logging.getLogger(__name__)


LOG_FILE_NAME = f"{SYLO_HOME}/sylo.log"
LOG_FILE_FORMAT = "%(asctime)s %(module)s %(levelname)s: %(message)s"
DEFAULT_LOG_LEVEL = logging.WARN


def logging_config(log_arg: str = None):
    if log_arg:
        log_level = log_arg
        handler = logging.StreamHandler(sys.stdout)
        logging.basicConfig(level=log_level, filename=LOG_FILE_NAME, filemode="w")

    else:
        log_level = DEFAULT_LOG_LEVEL
        handler = None
        logging.basicConfig(
            level=log_level,
        )

    if handler:
        logging.getLogger().addHandler(handler)
