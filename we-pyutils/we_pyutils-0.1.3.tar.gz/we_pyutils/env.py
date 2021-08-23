#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : env.py
@Time    : 2020-01-26 17:30
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2020 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import os


class GetEnv:
    DIRECT = 'Direct'
    DOCKER = 'Docker'
    ENV_PRIORITY = ['Project', 'Docker', 'Home']
    ENV_NAME = {
        'Project': 'project',
        'Docker': 'docker',
        'Home': 'home',
    }
    PROJECT_DIR = None
    HOME_DIR = None
    DOCKER_VOLUME_DIR = None
    DIR_LIST = []
    ENV_FILE_NAME = '.env'

    def __init__(self, dirs=None):
        if dirs and isinstance(dirs, list):
            self.DIR_LIST = dirs

    def get_running_env(self):
        docker_volume_exists = os.path.exists(self.DOCKER_VOLUME_DIR)
        if docker_volume_exists:
            return self.DOCKER
        else:
            return self.DIRECT

    def get_env(self, get_list=None):
        env_list = []
        for dir in self.DIR_LIST:
            ext = self.is_env_file_exists(dir)
            env_list.append(ext)
        if get_list:
            return env_list
        for env_path in env_list:
            if env_path:
                return env_path
        return None

    def is_env_file_exists(self, dir):
        env_path = os.path.join(dir, self.ENV_FILE_NAME)
        return env_path if self.is_file_exists(env_path) else None

    def is_file_exists(self, path):
        return True if os.path.exists(path) else False


if __name__ == '__main__':
    """
    测试用例
    """
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HOME_DIR = os.path.expanduser('~')
    dir_list = [
        BASE_DIR,
        HOME_DIR,
    ]
    e = GetEnv(dir_list)
    env_path = e.get_env(True)
    pass
