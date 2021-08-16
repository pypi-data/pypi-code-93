import logging
from logging.handlers import TimedRotatingFileHandler

import json_logging

from aide_sdk.logger.appender import JsonAppender


class LogManager:
    logger = None
    audit_logger = None

    @staticmethod
    def get_logger(log_level=logging.DEBUG):
        if LogManager.logger is None:
            LogManager.logger = LogManager._create_logger(
                "aide-logger",
                log_level=log_level,
                log_filename="aide.log")
        return LogManager.logger

    @staticmethod
    def _get_audit_logger(log_level=logging.DEBUG):
        if LogManager.audit_logger is None:
            LogManager.audit_logger = LogManager._create_logger(
                "aide-audit-logger",
                log_level=log_level,
                log_filename="aide-audit.log")
        return LogManager.audit_logger

    @staticmethod
    def _create_logger(logger_name=__name__, log_level=logging.DEBUG,
                       log_filename="aide.log"):
        json_logging.init_non_web(enable_json=True,
                                  custom_formatter=JsonAppender)

        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.addHandler(LogManager._create_stream_handler())
        logger.addHandler(LogManager._create_file_handler(log_filename))
        return logger

    @staticmethod
    def _create_stream_handler():
        return logging.StreamHandler()

    @staticmethod
    def _create_file_handler(log_filename):
        return TimedRotatingFileHandler(log_filename, when='midnight')
