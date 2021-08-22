import os
import socket
import logging
import logging.handlers
from .config import Config

# Logging 포맷 설정
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


def create_logger(namespace) -> logging.Logger:
    config = Config('olive-env.conf', 'worker-log')
    level = _get_log_level(config.get_value('level'))
    count = _get_log_count(config.get_value('rotate'))
    size = _get_log_bytes(config.get_value('size'))
    name = _get_log_name(namespace)

    logger = logging.getLogger('ovd-worker')
    logger.setLevel(level)
    file_handler = logging.handlers.RotatingFileHandler(filename=name, maxBytes=size, backupCount=count)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def _get_log_level(level_str):
    if level_str == 'info':
        level = logging.INFO
    elif level_str == 'warn':
        level = logging.WARNING
    elif level_str == 'error':
        level = logging.ERROR
    else:
        level = logging.DEBUG
    return level


def _get_log_count(rotate_str):
    return int(rotate_str)


def _get_log_bytes(size_str):
    i = size_str.find('kb')
    if i > 0:
        return int(size_str[:i]) * 1024
    i = size_str.find('mb')
    if i > 0:
        return int(size_str[:i]) * 1024 * 1024
    i = size_str.find('gb')
    if i > 0:
        return int(size_str[:i]) * 1024 * 1024 * 1024
    return 0


def get_log_path():
    return os.path.join(os.getenv('OLIVE_HOME'), 'worker/logs')


def _get_log_name(namespace):
    path = get_log_path()
    file = namespace + '@' + socket.gethostname() + '.log'
    return os.path.join(path, file)


