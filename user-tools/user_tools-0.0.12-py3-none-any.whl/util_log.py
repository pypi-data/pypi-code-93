#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_log.py
# @Time    : 2021-06-10
# @Author  : Skypekey


from functools import wraps
import logging
from logging.handlers import RotatingFileHandler


def get_logger(log_file, maxBytes=1024 * 1024 * 5):
    logger = logging.getLogger()  # 实例化一个logger对象
    logger.setLevel(logging.INFO)  # 设置初始显示级别
    # 创建一个文件句柄
    file_handle = RotatingFileHandler(filename=log_file,
                                      mode='a', encoding="UTF-8",
                                      backupCount=1,
                                      maxBytes=maxBytes)
    # 创建一个输出格式
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    file_handle.setFormatter(fmt)  # 文件句柄设置格式
    logger.addHandler(file_handle)  # logger对象绑定文件句柄
    return logger


def logger_tuple(func):
    """用于返回值为(True/False, "输出")的函数打印日志。"""

    @wraps(func)
    def with_logging(*args, **kwargs):
        logger = get_logger(kwargs["log_file"])
        result = func(*args, **kwargs)
        if result[0]:
            logger.info(result[1])
        else:
            logger.error(result[1])
        return result
    return with_logging


if __name__ == "__main__":
    pass
