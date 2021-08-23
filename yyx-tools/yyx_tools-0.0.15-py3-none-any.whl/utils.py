# -*- coding: utf-8 -*-
'''
@Time    : 2021/8/13
@Author  : Yanyuxiang
@Email   : yanyuxiangtoday@163.com
@FileName: utils.py
@Software: PyCharm
'''

import os
import yaml
from attrdict import AttrDict

def checkdir(dir_path):
    '''
    make dir if not exist

    :param dir_path: dir path to check
    :return: None
    '''
    os.makedirs(dir_path) if not os.path.isdir(dir_path) else None
    return

def load_yaml(yaml_path):
    # load config
    with open(yaml_path, 'r') as fopen:
        cfg = yaml.load(fopen)
        _show_config(cfg)
        return AttrDict(cfg)

def _show_config(m_dict):
    key_list = list(m_dict.keys())
    for k in key_list:
        if (isinstance(m_dict[k], dict)):
            _show_config(m_dict[k])
        else:
            print(f'--{k:20}: {m_dict[k]}')
    return