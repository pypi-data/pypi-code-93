import logging
import sys


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
