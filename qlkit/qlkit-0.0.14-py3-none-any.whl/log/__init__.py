#!/usr/bin/env python
# -*- coding:utf-8 -*-
import typing as t
import logging
import os
from logging.handlers import RotatingFileHandler
from ..config import Config

"""
基础的pykit logger 可以获取所有的日志，通过stream输出。
业务 logger 都在 pykit logger 的下一级。
pykit logger 有基础的formatter handler，业务logger可以定制自己的formatter handler，然后业务logger的信息
作为message传到pykit logger输出。

业务代码，不直接创建logger，只依赖一个logger。
"""


class ApplicationContextAdapter(logging.LoggerAdapter):
    """
    用于需要Application 上下文的logger，可以像其他logger一样使用。

    logger = logging.getLogger(name)
    context_logger = ApplicationContextAdapter(logger, app_local)
    context_logger.info("msg)
    """

    def process(self, msg, kwargs):
        """将 extra 的数据全部添加到日志中"""
        for k, v in self.extra.items():
            msg = " - [%s]:%s" % (k, v) + msg
        return msg, kwargs


def _get_root_logger(name: str = "pykit"):
    """for framework usage"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


def get_formatter(format_str: str):
    if format_str:
        return logging.Formatter(format_str)
    else:
        return logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )


def __get_file_handler(file_name: str, backup_count: int = 0,
                       max_bytes: int = 0) -> RotatingFileHandler:
    """
    一个按照文件大小切割的文件日志。
    :param file_name:
    :param backup_count: 备份日志文件个数
    :param max_bytes: 每个文件的大小
    :return:
    """
    if not backup_count:
        backup_count = 2
    if not max_bytes:
        max_bytes = 10240
    handler = RotatingFileHandler(
        file_name, maxBytes=max_bytes,
        backupCount=backup_count, encoding="utf-8"
    )
    return handler


def get_logger(log_name, config: Config,
               extra: t.Mapping[str, t.Any] = None):
    """
    获取一个文件日志
    extra 是一个dict-like的对象，在logger.info()输出的时候，会默认携带 extra 信息

    用法：
    from pykit.cmd import app_local
    from config import config
    logger = get_logger("logger_name", config, app_local)
    logger.info("msg")
    """
    root_logger = _get_root_logger()
    logger = root_logger.getChild(log_name)

    log_dir = config.get("logging_directory")
    if not log_dir:
        log_dir = "/tmp/log"
    file_handler = __get_file_handler(
        os.path.join(log_dir, "%s.log" % log_name),
        config.get("logging_backup_count"),
        config.get("logging_max_bytes")
    )
    file_handler.setFormatter(config.get("logging_format"))
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
    # check root handler
    if not root_logger.hasHandlers():
        file_handler = __get_file_handler(
            os.path.join(log_dir, "pykit.log"),
            config.get("logging_backup_count"),
            config.get("logging_max_bytes")
        )
        root_logger.addHandler(file_handler)

    if extra:
        return ApplicationContextAdapter(logger, extra)
    else:
        return logger
