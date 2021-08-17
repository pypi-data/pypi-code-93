#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Author: ChungNT
    Company: MobioVN
    Date created: 19/03/2021
"""
import logging
import os
import sys

from mobio.libs.Singleton import Singleton
from mobio.sdks.base.common import CONSTANTS
from mobio.sdks.base.common.system_config import SystemConfig
from mobio.sdks.base.configs import LoggingConfig, ApplicationConfig
from logstash_formatter import LogstashFormatterV1


class LOGGING:
    WRITE_TRACEBACK_FOR_ALL_CUSTOMIZE_EXCEPTION = "write_traceback_for_all_customize_exception"
    WRITE_TRACEBACK_FOR_GLOBAL_EXCEPTION = "write_traceback_for_global_exception"
    LOG_FOR_REQUEST_SUCCESS = "log_for_request_success"
    LOG_FOR_ALL_CUSTOMIZE_EXCEPTION = "log_for_all_customize_exception"
    LOG_FOR_GLOBAL_EXCEPTION = "log_for_global_exception"
    FILE_MAX_BYTES = "file_max_bytes"
    FILE_BACKUP_COUNT = "file_backup_count"


@Singleton
class MobioLogging:
    def __init__(self):

        if not LoggingConfig.K8S:
            logging.config.fileConfig(ApplicationConfig.LOG_CONFIG_FILE_PATH, None, disable_existing_loggers=False)

        self.logger = logging.getLogger('MOBIO')
        max_bytes = int(SystemConfig().get_section_map(CONSTANTS.LOGGING_MODE)[CONSTANTS.FILE_MAX_BYTES])
        backup_count = int(SystemConfig().get_section_map(CONSTANTS.LOGGING_MODE)[CONSTANTS.FILE_BACKUP_COUNT])
        if max_bytes > 0:
            try:
                os.makedirs(os.path.dirname(ApplicationConfig.LOG_FILE_PATH), exist_ok=True)
            except Exception as ex:
                print('WARNING:mobio_logging::__init__():make log dir: %s' % ex)
            self.logger.addHandler(logging.handlers.RotatingFileHandler(filename=ApplicationConfig.LOG_FILE_PATH,
                                                                        maxBytes=max_bytes,
                                                                        backupCount=backup_count))

        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(LogstashFormatterV1())
        logging.basicConfig(handlers=[handler], level=logging.DEBUG)

    @staticmethod
    def warning(content, log_key=None):
        content["log_key"] = log_key
        logging.warning(content)

    @staticmethod
    def debug(content, log_key=None):
        content["log_key"] = log_key
        logging.debug(content)

    @staticmethod
    def error(content, log_key=None):
        content["log_key"] = log_key
        logging.error(content)

    @staticmethod
    def info(content, log_key=None):
        content["log_key"] = log_key
        logging.info(content)
