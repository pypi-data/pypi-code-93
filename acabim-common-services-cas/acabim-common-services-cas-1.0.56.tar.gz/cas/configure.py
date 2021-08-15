import logging
import os
import sys
from multiprocessing import get_logger

ENVIRONMENT = os.getenv('PYTHON_ENVIRONMENT', 'development')


def configure_logging(upstream_loggers=None):
    upstream_loggers = [] if upstream_loggers is None else upstream_loggers
    format_str = '%(asctime)s [%(name)s]-{%(processName)s-%(threadName)s} %(levelname)s - %(message)s'
    log_level = logging.WARNING

    global ENVIRONMENT
    if is_staging():
        logging.basicConfig(level=logging.INFO, format=format_str, stream=sys.stdout)
        log_level = logging.ERROR
    elif is_production():
        logging.basicConfig(level=logging.INFO, format=format_str, stream=sys.stdout)
        log_level = logging.ERROR
    elif is_development():
        logging.basicConfig(level=logging.DEBUG, format=format_str, stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.DEBUG, format=format_str, stream=sys.stdout)
        ENVIRONMENT = 'Development'

    for logger in upstream_loggers:
        logging.getLogger(logger).setLevel(log_level)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=format_str))

    multiprocessLogger = get_logger()
    multiprocessLogger.setLevel(log_level)
    multiprocessLogger.addHandler(handler)


def is_development():
    return ENVIRONMENT.lower() == 'development'


def is_staging():
    return ENVIRONMENT.lower() == 'staging'


def is_production():
    return ENVIRONMENT.lower() == 'production'
