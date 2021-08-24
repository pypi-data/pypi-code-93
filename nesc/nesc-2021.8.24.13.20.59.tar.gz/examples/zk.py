#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : zk
# @Time         : 2021/2/7 9:43 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from meutils.zk_utils import *


if __name__ == '__main__':
    zk_watcher('/mipush/log')

    while 1:
        print(ZKConfig.info)

        time.sleep(3)


