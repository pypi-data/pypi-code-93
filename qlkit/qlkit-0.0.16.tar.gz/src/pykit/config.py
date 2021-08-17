#!/usr/bin/env python
# -*- coding:utf-8 -*-
import typing as t

DEFAULT_CONFIG = {
    "grpc_graceful_shutdown": 5,    # in seconds
    "grpc_ip": "localhost",
    "grpc_port": 8787,
    "grpc_workers": 2,
    "sqlalchemy_uri": "sqlite:///:memory:",
    "sqlalchemy_pool_size": 3,
    "sqlalchemy_max_overflow": 5,
    "logging_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "logging_directory": "/tmp/log",
    "logging_backup_count": 5,
    "logging_max_bytes": 102400,
}


class Config(dict):
    def __init__(self, config_dict: t.Optional[dict] = None) -> None:
        if config_dict is None:
            self.config_dict = DEFAULT_CONFIG
        else:
            self.config_dict = config_dict

        super(Config, self).__init__(self.config_dict)

    def __getitem__(self, item):
        raw_item = super(Config, self).__getitem__(item)
        if raw_item is None:
            return DEFAULT_CONFIG.get(item)
        else:
            return raw_item
