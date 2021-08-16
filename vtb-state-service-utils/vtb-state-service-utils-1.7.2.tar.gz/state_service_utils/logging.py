import logging.handlers
import os

from vtb_py_logging import OrderJsonFormatter, OrderConsoleFormatter


def create_logger(logger_name: str):
    if not logging.getLogger(logger_name).hasHandlers():
        LOG_DIR_PATH = os.getenv('LOG_DIR_PATH', f'/var/log/{logger_name}')
        os.makedirs(LOG_DIR_PATH, exist_ok=True)

        LOG_FILE_NAME = os.getenv('LOG_FILE_NAME', f'{logger_name}.log')
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(OrderConsoleFormatter())

        jh = logging.handlers.TimedRotatingFileHandler(when='H', interval=1, backupCount=1,
                                                       filename=f'{LOG_DIR_PATH}/{LOG_FILE_NAME}')
        jh.setLevel(logging.INFO)
        jh.setFormatter(OrderJsonFormatter())

        logger.addHandler(ch)
        logger.addHandler(jh)
        return logger
    else:
        return logging.getLogger(logger_name)
