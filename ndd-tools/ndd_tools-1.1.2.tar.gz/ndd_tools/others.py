# -*- coding: utf-8 -*-
import os
import json
from .data_models import ProxyModel, ApiClientConfig


def load_config(config_file_path: str):
    with open(config_file_path, 'r') as f:
        data = json.load(f)
        return ApiClientConfig(**data)


def add_proxy(config: ProxyModel):
    os.environ['http_proxy'] = config.http_proxy
    os.environ['https_proxy'] = config.https_proxy
    if os.getenv('no_proxy'):
        os.environ['no_proxy'] = os.getenv('no_proxy') + ',' + config.no_proxy
    else:
        os.environ['no_proxy'] = config.no_proxy


def create_directory(dir_path: str):
    # create directories for log file
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
