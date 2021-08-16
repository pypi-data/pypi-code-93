import logging
import sys


def setup_log() -> None:
    log_format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s] - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(log_format)
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])
