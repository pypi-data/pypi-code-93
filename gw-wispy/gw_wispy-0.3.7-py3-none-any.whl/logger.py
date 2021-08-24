import sys
import logging


def init_logger(level=0):
    """setup logging

    Keyword Arguments:
        level {int} -- either 0, 1 or 2. (default: {0})
            0: WARNING
            1: INFO
            2: DEBUG

    Returns:
        logger -- logger object
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # need to do this to avoid print things twice
    # https://stackoverflow.com/a/6729713/12840171
    # and this to setup levels
    # https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.flush = sys.stdout.flush
        if level == 0:
            handler.setLevel(logging.WARNING)
        elif level == 1:
            handler.setLevel(logging.INFO)
        elif level == 2:
            handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logger.handlers[0].formatter = formatter
        if level == 0:
            logger.setLevel(logging.WARNING)
        elif level == 1:
            logger.setLevel(logging.INFO)
        elif level == 2:
            logger.setLevel(logging.DEBUG)
        logger.handlers[0].flush()

    return logger
