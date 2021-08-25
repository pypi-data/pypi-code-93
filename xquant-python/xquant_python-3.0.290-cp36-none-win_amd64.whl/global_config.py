#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from os.path import dirname, join, expanduser, abspath

USER_HOME: str = expanduser('~')
INSTALL_DIR: str = dirname(abspath(__file__))
DEF_CONFIG_DIR: str = '.xquant'
SSL_PROPERTIES_FILE = 'ssl.properties'
BUNDLED_DIR: str = 'bundled'
SERVER_DIR: str = 'server'
config_dir: str = join(USER_HOME, DEF_CONFIG_DIR)
config_file: str = 'config.json'
cache_dir: str = ''
bar_column = ['symbol', 'trade_date', 'time_stop', 'suspend', 'close', 'high',
              'low', 'open', 'pre_close', 'settle', 'pre_settle',
              'volume', 'turnover', 'total_volume', 'total_turnover', 'position']
bar_columns = ['close', 'high',
               'low', 'open', 'pre_close', 'settle', 'pre_settle',
               'volume', 'turnover', 'total_volume', 'total_turnover', 'position']

callback = {"on_initialize", "on_before_market_open",
            "on_tick", "on_first_tick", "on_bar",
            "on_handle_data", "on_terminate",
            "on_timer", "on_order_update"}


def get_download_cache_dir() -> str:
    """Returns full path to download cache directory."""

    if cache_dir:
        return cache_dir

    return join(config_dir, 'cache')



