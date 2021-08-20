#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/19 11:39
# @Author  : 江斌
# @Software: PyCharm
import os
import logging
import shutil


def get_logger(app_name, log_file='data.log'):
    if os.path.exists(log_file):
        shutil.copy(log_file, log_file + ".old")
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(process)d:%(thread)d %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s")  # or whatever
    handler = logging.FileHandler(log_file, "w", "utf-8")  #
    handler.setFormatter(formatter)  # Pass handler as a parameter, not assign
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.removeHandler(root_logger.handlers[0])
    logger = logging.getLogger(app_name)
    return logger
