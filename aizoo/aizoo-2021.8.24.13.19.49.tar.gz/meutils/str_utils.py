#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : str_utils
# @Time         : 2020/11/12 1:48 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


def str_replace(s: str, dic: dict):
    """多值替换
        str_replace('abcd', {'a': '8', 'd': '88'})
    """
    return s.translate(str.maketrans(dic))


def unquote(s='%E6%9C%80%E6%96%B0%E6%9C%8D%E5%8A%A1'):
    """http字符串解码"""
    from urllib import parse

    return parse.unquote(s)


if __name__ == '__main__':
    print(str_replace('abcd', {'a': '8', 'd': '88'}))
    print(unquote())
