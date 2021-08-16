#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : try
# @Time         : 2021/4/2 11:03 上午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :
from meutils.pipe import *
from meutils.log_utils import logger4feishu


def feishu_catch(more_info=True):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        try:
            return wrapped(*args, **kwargs)

        except Exception as e:
            info = traceback.format_exc() if more_info else e
            logger4feishu(wrapped.__name__, info)

    return wrapper


if __name__ == '__main__':
    @feishu_catch()
    def f():
        1 / 0


    f()
