#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : file.py
@Time    : 2020-02-09 7:01
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2020 WingEase Technology Co.,Ltd. All Rights Reserved.
"""

from os import listdir
from os.path import isfile, join, splitext


# 获取文件列表（支持指定扩展名）
def get_file_list(dir_path, extension_list=None):
    file_list = []
    for f in listdir(dir_path):
        if isfile(join(dir_path, f)):
            if extension_list is None or extension_list == []:
                file_list.append(f)
            else:
                if splitext(f)[1] in extension_list:
                    file_list.append(f)
    return file_list
