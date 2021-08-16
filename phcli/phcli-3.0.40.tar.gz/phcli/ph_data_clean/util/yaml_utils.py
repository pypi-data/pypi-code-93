# -*- coding: utf-8 -*-

import os
import yaml
from phcli.ph_errs.ph_err import PhException


def load_by_file(file):
    """
    从文件加载 yaml 文件
    :return: obj 对象实体
    """
    with open(file, encoding='UTF-8') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def append_to_file(obj, file):
    """
    追加写入 yaml 文件
    """
    with open(file, 'a', encoding='UTF-8') as file:
        yaml.dump(obj, file, default_flow_style=False, encoding='utf-8', allow_unicode=True)


def override_to_file(obj, file):
    """
    覆盖写入 yaml 文件
    """
    with open(file, 'w', encoding='UTF-8') as file:
        yaml.dump(obj, file, default_flow_style=False, encoding='utf-8', allow_unicode=True)


def load_by_dir(dir):
    """
    从目录加载多个 yaml 文件
    :return: list[obj] 对象实体列表
    """
    # 参数不是目录，直接返回
    if not os.path.isdir(dir):
        raise PhException("args not is dir")

    if not dir.endswith("/"):
        dir = dir + "/"

    lst = []
    for sub in os.listdir(dir):
        file = dir + sub
        if not (os.path.isfile(file) or file.endswith('.yaml')):
            continue

        obj = load_by_file(file)
        if isinstance(obj, list):
            lst += obj
        else:
            lst.append(obj)

    return lst
