#!/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function
from builtins import (bytes, str, super, range, zip, round, pow, object)

import signal

from ._time import *
from .api import *
from .data import *
from .global_config import *


class StrategyProxy:
    def __init__(self):
        self.api = StrategyApi.create_strategy_api()
        self.spi = None
        self.progress = DownloadProgress()

    def __del__(self):
        self.api.exit()
        self.api = None
        self.progress = None
        self.spi = None

    def run_quant(self, js):
        import json
        try:
            self.load_str(json.dumps(js))

            while True:
                run_once = self.api.wait_for_shutdown(500)
                if run_once != 0:
                    break
            self.api.exit()
        except Exception as e:
            self.api.exit()
            raise e
        return 0

    def load_str(self, json_str):
        import json
        import sys

        config_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
        base_config = json.loads(json_str)

        strategy_file = sys.argv[0]
        if 'strategy_file' in base_config:
            strategy_file = base_config['strategy_file']

        advance_config = check_config(base_config, config_path)

        # 脱离平台自动创建
        if 'auto_create' not in base_config or not base_config['auto_create']:
            if 'instance_id' not in base_config:
                base_config['instance_id'] = input("instance_id: ")

        # 日志模块必须放在最开始初始化
        from .tools import LogHandler
        import logging
        LogHandler.init(log_path=advance_config.logpath, console=advance_config.console)
        LogHandler.set_log_level(logging.INFO)

        # 如果用户指定了日志级别，则以用户指定的日志级别为准
        loglevel = advance_config.loglevel
        loglevel = loglevel.upper()
        if loglevel != "":
            if loglevel == "DEBUG":
                LogHandler.set_log_level(logging.DEBUG)
            elif loglevel == "ERROR":
                LogHandler.set_log_level(logging.ERROR)

        self.spi = FileAnalyzerSpi(strategy_file)
        self.api.reg_analyzer(self.spi)

        rc = self.api.init(json.dumps(base_config))
        if rc != 0:
            raise Exception("init fail, error:" + StrategyApi.error_code_to_string(rc))


def version():
    return StrategyApi.get_version()


def load_config(path):
    """
    读取配置文件
    :param path: 配置文件地址
    :return:
    """
    from .utils import commonjson
    jsonstr = ""
    with open(path, 'r') as reader:
        jsonstr = reader.read()
    return commonjson.loads(jsonstr)


def run_quant(config):
    """
    直接读取config(json格式)
    :param config: json格式配置
    :return:
    """
    app = StrategyProxy()
    ret = app.run_quant(config)
    app = None
    return ret


def create_data_imp():
    data_obj = None

    def wrapper(json_str):
        nonlocal data_obj
        if data_obj is None:
            if isinstance(json_str, str):
                obj = DataApi.create_api_by_json(json_str)
            else:
                import json
                obj = DataApi.create_api_by_json(json.dumps(json_str))
            data_obj = DataProxy(obj)
        return data_obj

    return wrapper


create_data = create_data_imp()
