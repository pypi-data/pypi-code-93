import inspect
import logging
import os
from Util.JobHelper import *


class StructuredMessage(object):
    """docstring for StructuredMessage"""

    def __init__(self, subject, detail):
        super(StructuredMessage, self).__init__()
        self.subject = subject
        self.detail = detail

    def __str__(self):
        return '{}  {}'.format(self.subject, self.detail)


class Log(object):
    def __init__(self, log_name):
        self.log_name = log_name
        self.logger = self.init_log()
        # self._ = StructuredMessage
        self.error_list = []

    def init_log(self):
        logger = logging.getLogger(self.log_name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # todo add json part of log later, for elk search
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def info(self, subject, detail=''):
        message = ' - '.join([str(subject), str(detail), self.get_dynamic_info()])
        self.logger.info(message)

    def error(self, subject, detail=''):
        message = ' - '.join([str(subject), str(detail), self.get_dynamic_info()])
        self.logger.error(message)
        self.error_list.append((subject, detail))

    def warn(self, subject, detail=''):
        message = ' - '.join([str(subject), str(detail), self.get_dynamic_info()])
        self.logger.warn(message)

    def get_dynamic_info(self):
        stack = inspect.stack()
        parent = get_stack_frame(stack)
        frame, file, line, method, _, _ = parent
        source_file = file.split(r"/")[-1]
        return '{} - {} - {}'.format(source_file, line, method)
