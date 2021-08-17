# -*- coding: utf-8 -*-
'''
@Time    : 2021/8/13
@Author  : Yanyuxiang
@Email   : yanyuxiangtoday@163.com
@FileName: utils.py
@Software: PyCharm
'''

import os

def checkdir(dir_path):
    '''
    make dir if not exist

    :param dir_path: dir path to check
    :return: None
    '''
    os.makedirs(dir_path) if not os.path.isdir(dir_path) else None
    return