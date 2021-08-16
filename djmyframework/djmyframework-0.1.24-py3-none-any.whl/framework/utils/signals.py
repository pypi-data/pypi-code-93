# -*- coding: utf-8 -*-
# @Time    : 2021-03-29 12:38
# @Author  : xzr
# @File    : signal
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 
from __future__ import absolute_import

import io
import os
import signal
import time
import traceback


def trace_msg():
    """跟踪消息
    """
    fp = io.StringIO()
    traceback.print_exc(file=fp)
    message = fp.getvalue()
    return message


_signal_handlers = {}


def _signal_multiple_handler(sig, frame):
    for handler in _signal_handlers.get(sig, []):
        try:
            handler(sig, frame)
        except Exception as e:
            print(trace_msg)


def add_signal_handler(signal_num, handler, is_first=True):
    """
    allowing to register multiple handlers for the same signal
    :param signal_num: kill -l
    :param handler: 处理函数
    :param is_first: 是否优先处理
    :return: None
    """
    _signal_handlers.setdefault(signal_num, [])
    old_handler = signal.getsignal(signal_num)
    if old_handler != _signal_multiple_handler:
        _signal_handlers[signal_num].append(old_handler)

    if is_first:
        _signal_handlers[signal_num].insert(0, handler)
    else:
        _signal_handlers[signal_num].append(handler)

    signal.signal(signal_num, _signal_multiple_handler)


if __name__ == '__main__':
    def a(sig, frame):
        print(1)
        print(sig, frame)


    def b(sig, frame):
        print(2)
        print(sig, frame)


    add_signal_handler(signal.SIGHUP, a)
    add_signal_handler(signal.SIGHUP, b,False)
    print(signal.getsignal(signal.SIGHUP))
    print(os.getpid())
    while 1:
        time.sleep(1)
