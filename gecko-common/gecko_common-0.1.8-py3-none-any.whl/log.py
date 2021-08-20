import logging
from logging import Logger
import sys


logging_pool = dict()


def create_logger(name: str = "root", file_path="") -> Logger:
    if name in logging_pool:
        return logging_pool[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s (%(levelname)s) - [%(filename)s:%(lineno)d]: %(message)s",
        datefmt='%y-%m-%d %H:%M:%S'
    )

    if file_path:
        fh = logging.FileHandler(file_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    logging_pool[name] = logger
    return logger
