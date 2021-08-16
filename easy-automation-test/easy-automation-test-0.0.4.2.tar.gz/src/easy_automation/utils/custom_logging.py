#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/14
# import datetime

import logging
import logging.handlers
import os

from ..utils.common import find_project_root_dir


class Logs:
    _log_instance = {}

    def __init__(self, log_name='easy-automation'):
        if log_name not in self._log_instance:
            _log = logging.getLogger(log_name)
            formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s'
                                          ': %(message)s',
                                          datefmt='%Y-%m-%d %H:%M:%S')
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            sh.setLevel(logging.INFO)

            logs_dir = os.path.join(find_project_root_dir(), 'logs')
            if not os.path.exists(logs_dir):
                os.mkdir(logs_dir)
            log_file = os.path.join(logs_dir, 'log.log')
            fh = logging.handlers.RotatingFileHandler(filename=log_file, mode='a', maxBytes=8 * 1024 * 20)
            fh.setFormatter(formatter)
            fh.setLevel(logging.DEBUG)

            _log.setLevel(logging.DEBUG)
            _log.addHandler(sh)
            _log.addHandler(fh)
            self._log_instance[log_name] = _log

        self._log = self._log_instance[log_name]

    def debug(self, msg, *args, **kwargs):
        self._log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log.critical(msg, *args, **kwargs)







