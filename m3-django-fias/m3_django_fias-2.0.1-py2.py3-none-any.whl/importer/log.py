# coding: utf-8
from __future__ import unicode_literals, absolute_import

import datetime
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from django.conf import settings


class Log(object):

    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __init__(self):
        self.level = Log.INFO

        self._status = ''

    def _get_status(self):
        return self._status

    def _set_status(self, value):
        self.info(value)

        self._status = value
    status = property(fget=_get_status, fset=_set_status)

    def trace(self, message):
        print(message)

    def debug(self, message):
        if self.level == Log.DEBUG:
            self.trace('DEBUG: {0}'.format(message))

    def error(self, message):
        if self.level <= Log.ERROR:
            self.trace('ERROR: {0}'.format(message))

    def warning(self, message):
        if self.level <= Log.WARNING:
            self.trace('WARNING: {0}'.format(message))

    def info(self, message):
        if self.level <= Log.INFO:
            self.trace('INFO: {0}'.format(message))

    def progress(self):
        if self.level == Log.INFO:
            sys.stdout.write('.')
            sys.stdout.flush()


log = Log()


def get_file_logger():
    """
    Возвращает логгер в файл
    """
    logs_folder = os.path.join(settings.PROJECT_PATH, 'logs')
    log_file = 'fias_{}_{}.log'.format(
        datetime.date.today().strftime('%d.%m.%Y'),
        str(len(os.listdir(logs_folder)) + 1),
    )
    log_path = os.path.join(logs_folder, log_file)
    formatter = logging.Formatter(
        "\n%(pathname)s:%(lineno)d\n[%(asctime)s] %(levelname)s: %(message)s",
        '%Y-%m-%d %H:%M:%S',
    )

    handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, encoding='utf-8')
    handler.setFormatter(formatter)

    logger = logging.getLogger('fias')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    return logger


file_logger = get_file_logger()
