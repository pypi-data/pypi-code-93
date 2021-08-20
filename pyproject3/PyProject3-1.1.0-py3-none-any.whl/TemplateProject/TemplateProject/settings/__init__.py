#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/18 18:05
# @Author  : 江斌
# @Software: PyCharm

import os
from .yaml_config import YamlConfig
from .log_config import get_logger

YAML_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")
YAML_CONFIG = YamlConfig(YAML_FILE)
LOG_FILE = YAML_CONFIG.get_value('log_file')
APP_NAME = YAML_CONFIG.get_value('app_name')
logger = get_logger(app_name=APP_NAME, log_file=LOG_FILE)

# logger.level = logging.DEBUG
