#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, super, object)
import collections
import re
import time
import sys
from xquant.lib import *
from xquant._time import EtaTime

__py_version__ = sys.version_info.major


class StrategyException(Exception):
    pass


class EtaDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


def check_symbol(symbol, default=None):
    if not isinstance(symbol, str):
        if default is None:
            raise StrategyException("invalid symbol argument, expect string")
        else:
            symbol = default
    return symbol



def conv_list_str(l):
    return [s.encode('utf-8') for s in l]


def check_msg(msg, default=None):
    if not isinstance(msg, str):
        if default is None:
            raise StrategyException("invalid msg argument, expect string")
        else:
            msg = default
    return msg


def check_indexs(indexs):
    new_indexs = []
    if isinstance(indexs, str):
        new_indexs.append(indexs)
    elif isinstance(indexs, collections.Iterable):
        return conv_list_str(indexs)
    elif isinstance(indexs, list):
        return conv_list_str(indexs)
    else:
        raise StrategyException("invalid index argument, expect string or list<string>")

    return new_indexs


def check_market(index):
    if index is None:
        index = "CS"
    elif not isinstance(index, str):
        raise StrategyException("invalid symbol argument, expect string")

    return index


def check_symbols(symbols, no_throw=False):
    new_symbols = []
    if type(symbols) == str:
        new_symbols.append(symbols)
    elif isinstance(symbols, collections.Iterable):
        new_symbols = conv_list_str(symbols)
    elif isinstance(symbols, set):
        new_symbols = conv_list_str(symbols)
    elif not no_throw:
        raise StrategyException("invalid symbols argument, expect string or list<string>")

    return new_symbols


def check_field(field):
    if type(field) != str:
        raise StrategyException("invalid field argument, expect string")

    return field


def check_fields(fields, default_field=None):
    new_fields = []
    if fields is None:
        if default_field is None:
            raise StrategyException("invalid fields argument, expect string or list<string>")
        else:
            return default_field

    elif type(fields) == str:
        new_fields.append(fields)
    elif isinstance(fields, collections.Iterable):
        return conv_list_str(fields)
    elif isinstance(fields, list):
        return conv_list_str(fields)
    else:
        raise StrategyException("invalid fields argument, expect string or list<string>")

    return new_fields


def check_bar_sets(bar_sets):
    n_bar_sets = []
    if bar_sets is not None:
        if isinstance(bar_sets, list):
            for bar_set in bar_sets:
                n_bar_sets.append(check_bar_set(bar_set))
        elif isinstance(bar_sets, tuple):
            n_bar_sets.append(check_bar_set(bar_sets))

    return n_bar_sets


def check_bar_set(bar_set):
    if isinstance(bar_set, tuple):
        if len(bar_set) == 2:
            if isinstance(bar_set[0], EBarTimespan) and isinstance(bar_set[1], int):
                return bar_set

    raise StrategyException("invalid bar set argument, expect tuple(EBarTimespan, int)")


def is_valid_date(trade_date):
    """判断是否是一个有效的日期字符串"""
    try:
        if re.match(r'[1-3]\d\d\d[0-2]\d[0-3]\d', str(trade_date)) is None:
            return False

        time.strptime(str(trade_date), "%Y%m%d")
        return True
    except:
        return False


def check_trade_date(trade_date, default=None, name=None):
    date_name = "trading day"
    if isinstance(trade_date, EtaTime):
        return trade_date.date

    if type(name) == str:
        date_name = name
    if trade_date is None:
        if default is None:
            raise StrategyException("invalid %s argument, expect int" % date_name)
        else:
            trade_date = default
    elif not isinstance(trade_date, int):
        raise StrategyException("invalid %s argument, expect int" % date_name)
    elif not is_valid_date(trade_date):
        raise StrategyException("invalid %s:%s argument, expect YYYYmmdd" % (date_name, trade_date))
    elif default is not None and trade_date > default:
        raise StrategyException("future " + date_name + ": %d" % trade_date)

    return trade_date


def check_count(count, default=None):
    if count is None:
        if default is None:
            count = default
        elif not isinstance(default, int):
            raise StrategyException("invalid count argument, expect int")
        elif default < 1:
            raise StrategyException("count should be greater than 0")
    elif not isinstance(count, int):
        raise StrategyException("invalid count argument, expect int")
    elif count < 1:
        raise StrategyException("count should be greater than 0")

    return count


def check_enum(enum, enum_set, default=None, name=None):
    if name is None:
        name = enum

    if enum is None:
        if default is None:
            raise StrategyException("invalid %s argument, expect int" % name)
        else:
            enum = default
    elif not isinstance(enum, int):
        raise StrategyException("invalid %s argument, expect int" % name)
    elif enum not in enum_set:
        raise StrategyException("error %s" % name)

    return enum


def check_real_enum(enum, enum_type, name):
    if not isinstance(enum, enum_type):
        raise StrategyException("invalid enum argument, expect %s enum" % name)
    return enum


def check_report(report):
    if report is None:
        return ""
    elif type(report) != str or re.match(r'[1-3]\d\d\dQ[1-4]', report) is None:
        raise StrategyException("invalid report argument")

    return report


def check_position_side(span):
    if not isinstance(span, EPositionSide):
        raise StrategyException("invalid Position Side argument, expect EPositionSide enum")

    return span


def check_columns(columns, needs, all):
    if columns is None:
        if all is None:
            raise StrategyException("invalid columns argument, expect string or list")
        else:
            return all
    elif type(columns) == str:
        if columns in all:
            needs.append(columns)
            return needs
        else:
            raise StrategyException("invalid columns argument, please check your input")
    elif isinstance(columns, list):
        new_columns = set(all)
        if [False for c in columns if c not in new_columns]:
            raise StrategyException("invalid columns argument, please check your input")
        else:
            needs.extend(list((set(columns) - set(needs))))
            return needs
    else:
        raise StrategyException("invalid columns argument, expect string or list")


def check_data_frame(data_frame):
    if not isinstance(data_frame, bool):
        raise StrategyException("invalid dataFrame argument, expect bool")

    return data_frame


def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value):
            pr[name] = value
    return pr


def check_config(conf, config_path):
    config = EtaDict({})

    config.console = 0 if "console" not in conf else conf['console']
    config.loglevel = 'INFO' if "log_level" not in conf else conf['loglevel']
    config.logpath = (config_path + "/logs/") if "logpath" not in conf else conf['logpath']

    return config


def check_valid_percent(percent):
    if not 0 <= percent <= 1:
        raise StrategyException("invalid percent, expect range[0~1]")
    return True


def check_time_ranges(time_ranges):
    ranges = []
    if time_ranges is not None:
        if isinstance(time_ranges, list):
            for t in time_ranges:
                ranges.append(check_time_range(t))
        elif isinstance(time_ranges, tuple):
            ranges.append(check_time_range(time_ranges))

    return ranges


def check_time_range(time_range):
    if isinstance(time_range, tuple):
        if len(time_range) == 2:
            if isinstance(time_range[0], str) and isinstance(time_range[1], str) and len(time_range[0]) == 5 and len(
                    time_range[1]) == 5:
                return time_range
    raise StrategyException("invalid time range set argument, expect like [('09:51','09:55'),('14:10','15:10')]")


def check_str(token, default=None):
    if type(token) != str:
        if default is None:
            raise StrategyException("invalid token argument, expect string")
        else:
            token = default
    return token
