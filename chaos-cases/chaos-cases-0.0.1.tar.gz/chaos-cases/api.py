#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .main import Chaos


def chaos(params, custom, type="product"):
    """
    :param params:参数列表 ["name", "age","sex","like"]
    :param custom:自定义参数值 {"name": "zhangsan","like":"qiu"}
    :param type:
                product 笛卡尔积　　（有放回抽样排列）
                permutations 排列　　（不放回抽样排列）
                combinations 组合,没有重复　　（不放回抽样组合）
                combinations_with_replacement 组合,有重复　　（有放回抽样组合）
    :return:
    """
    return Chaos.chaos(params, custom, type=type)
