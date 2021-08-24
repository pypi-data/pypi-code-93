#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
doc:
"""
import sys
import logging

fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def display(log=None, debug=True):
    if not debug:
        return
    # 日志输出
    log.debug('debug message')
    log.info('info message')
    log.error('error message')
    log.critical('critical message')


def conf_logger(log=None, debug=True):
    if not isinstance(log, logging.Logger):
        return
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    display(log, debug)


if __name__ == '__main__':
    logger = logging.getLogger('debug')
    # print("--", type(logger))
    conf_logger(logger)
