#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : json_utils
# @Time         : 2021/4/22 1:51 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : pd.io.json.json_normalize
# https://github.com/ijl/orjson#quickstart
# https://jmespath.org/tutorial.html


def json2class(dic, class_name='Test'):

    s = "\n\t".join([f"{k} = {v}" for k, v in dic.items()])
    print(f"""
    class {class_name}(object):
        {s}
    """)
