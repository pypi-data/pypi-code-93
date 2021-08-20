import logging
from typing import Optional

LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def init_logs():
    """Run logging initialization (before loading log level)"""
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, datefmt=LOG_DATE_FORMAT)


def configure_logs(verbosity: int = 0, log_level: Optional[str] = None):
    """Configure root logger with a log level"""
    if log_level is None:
        if verbosity > 0:
            level = logging.DEBUG
        else:
            level = logging.INFO
    else:
        level = _get_logging_level(log_level)
    logging.basicConfig(format=LOG_FORMAT, level=level, datefmt=LOG_DATE_FORMAT)


def _get_logging_level(str_level: str) -> int:
    return {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL,
        'off': logging.NOTSET,
    }[str_level.lower()]
