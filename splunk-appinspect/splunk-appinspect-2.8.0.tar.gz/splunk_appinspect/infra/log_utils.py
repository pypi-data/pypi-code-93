# Copyright 2019 Splunk Inc. All rights reserved.

"""
Splunk AppInspect logger utility module
"""

# Python Standard Libraries
import logging
import six


def configure_logger(logger, log_level, log_file):
    """Intended to be used for the configuring the root logger of Python's
    logging library.
    """
    logging_message_format = (
        'LEVEL="%(levelname)s"'
        ' TIME="%(asctime)s"'
        ' NAME="%(name)s"'
        ' FILENAME="%(filename)s"'
        ' MODULE="%(module)s"'
        ' MESSAGE="%(message)s"'
    )
    handler_formatter = logging.Formatter(fmt=logging_message_format, datefmt=None)

    if log_file is not None:

        if six.PY2:
            logging_handler = logging.FileHandler(
                log_file, mode="ab+", encoding="ascii", delay=False
            )
        else:
            logging_handler = logging.FileHandler(
                log_file, mode="a+", encoding="ascii", delay=False
            )
    else:
        # Default to STDOUT
        logging_handler = logging.StreamHandler(stream=None)

    logging_handler.setFormatter(handler_formatter)

    logger.handlers = []
    logger.addHandler(logging_handler)
    logger.setLevel(log_level)
