#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, super, range, zip, round, pow, object)

import sys
import os
import logging
import logging.handlers
from ._checkparam import EtaDict

__all__ = ['LOG', 'log', 'LogHandler']


def default_print(*objects):
    sep = None
    end = None
    file = None
    flush = False
    if sep is None:
        sep = ' '
    if end is None:
        end = '\n'
    if file is None:
        file = sys.stdout
    file.write(sep.join(map(str, objects)) + end)
    if flush:
        file.flush()


# 其他模块调用时，直接使用LOG


LOG = EtaDict({})
LOG.DEBUG = default_print
LOG.INFO = default_print
LOG.WARN = default_print
LOG.ERROR = default_print

log = EtaDict({})
log.debug = default_print
log.info = default_print
log.warn = default_print
log.error = default_print


class LogHandler:
    fmt = "[%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(thread)d] %(message)s"
    formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")

    # add handler and formatter to logger
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    console = True
    app = "algo"
    log_path = "/tmp/algo/log"

    @staticmethod
    def init(log_path="", console=True, level=None):
        if log_path != "":
            LogHandler.log_path = log_path
        if not os.path.exists(LogHandler.log_path):
            os.makedirs(LogHandler.log_path)

        LogHandler.LOGGER_MAIN = LogHandler.create_day_logger(file_name='python_main', console=console)

        global LOG

        LOG.DEBUG = LogHandler.LOGGER_MAIN.debug
        LOG.INFO = LogHandler.LOGGER_MAIN.info
        LOG.WARN = LogHandler.LOGGER_MAIN.warn
        LOG.ERROR = LogHandler.LOGGER_MAIN.error
        LOG.ANY = LogHandler.LOGGER_MAIN.critical

        global log

        log.debug = LogHandler.LOGGER_MAIN.debug
        log.info = LogHandler.LOGGER_MAIN.info
        log.warn = LogHandler.LOGGER_MAIN.warn
        log.error = LogHandler.LOGGER_MAIN.error
        log.any = LogHandler.LOGGER_MAIN.critical

        if level is not None:
            LogHandler.set_log_level(level)

    @staticmethod
    def set_log_level(level=logging.DEBUG):
        LogHandler.LOGGER_MAIN.setLevel(level)

    @staticmethod
    def create_roll_logger(file_name='default_roll', console=False, file_limit=100, level=logging.DEBUG, back_cnt=5):
        """
        file limit 单位 (M)
        """
        log_name = LogHandler.log_path + "/" + LogHandler.app + "." + str(file_name) + '.log'
        # mode默认mode='a'
        handler = logging.handlers.RotatingFileHandler(log_name, maxBytes=file_limit * 1024 * 1024,
                                                       backupCount=back_cnt,
                                                       mode='a')
        fmt = LogHandler.fmt
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger = logging.getLogger(str(file_name))
        logger.addHandler(handler)
        if console:
            logger.addHandler(LogHandler.stdout_handler)

        logger.setLevel(level)
        return logger

    @staticmethod
    def create_day_logger(file_name='default_day', console=False, level=logging.DEBUG, back_cnt=365):
        log_name = LogHandler.log_path + "/" + LogHandler.app + "." + str(file_name) + '.log'
        handler = logging.handlers.TimedRotatingFileHandler(log_name, when="midnight", interval=1, backupCount=back_cnt)
        # handler.mode = 'w'
        handler.suffix = "%Y-%m-%d"
        fmt = LogHandler.fmt
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger = logging.getLogger(str(file_name))
        logger.addHandler(handler)
        if console:
            logger.addHandler(LogHandler.stdout_handler)
        logger.setLevel(level)
        return logger
