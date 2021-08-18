import os
import logging

LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'silly': 0
}
log_level_key = os.environ.get('LOG_LEVEL', 'critical')
log_level = LOG_LEVELS.get(log_level_key)

print('LOG_LEVEL: {}'.format(log_level_key))

logger = logging.getLogger()
logger.setLevel(log_level)