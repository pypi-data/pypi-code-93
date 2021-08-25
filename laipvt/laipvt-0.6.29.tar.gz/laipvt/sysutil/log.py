from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
from logging import handlers
from logging.handlers import RotatingFileHandler as RFHandler


class Logger():
    """
        日志记录类
    """

    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    log_fmt = '[%(levelname)s] %(asctime)s %(filename)s [line:%(lineno)d] %(funcName)s: %(message)s'

    def __init__(self, log_path="/var/log/laipvt", log_name="laipvt.log", log_level="debug", fmt=log_fmt, back_count=3, tty=False):

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        file_name = os.path.join(log_path, log_name)
        format_str = logging.Formatter(fmt)

        self.logger = logging.getLogger(file_name)
        self.logger.setLevel(self.level_relations.get(log_level.lower()))
        file_handler = handlers.TimedRotatingFileHandler(filename=file_name,
                                               when="D",
                                               backupCount=back_count,
                                               encoding='utf-8')
        file_handler.setFormatter(format_str)
        self.logger.addHandler(file_handler)
        if tty:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(format_str)
            self.logger.addHandler(stream_handler)

    def get(self):
        return self.logger