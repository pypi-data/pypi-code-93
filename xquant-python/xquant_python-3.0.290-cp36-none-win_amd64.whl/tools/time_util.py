#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, super, range, zip, round, pow, object)

import time
import datetime
import math


def ms_to_time_str(timestamp):
    time_array = time.localtime(timestamp / 1000)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time


def ms_to_time_string(timestamp):
    time_array = time.localtime(timestamp / 1000)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time


def __from_date_integer(dt):
    y = int(dt / 10000)
    m = int(dt / 100 - y * 100)

    return (y, m, int(dt - y * 10000 - m * 100))


def __from_time_integer(tm):
    s = int(tm / 10000)
    m = int(tm / 100 - s * 100)

    return (s, m, int(tm - s * 10000 - m * 100))


def __to_date(dt):
    y, m, d = __from_date_integer(dt)
    return datetime.date(y, m, d)


def __to_date_integer(y, m, day):
    iY = y
    iM = m
    if m < 1:
        iM = 1
    elif m > 12:
        iM = 12
    if y < 1900:
        iY = 2010
    return iY * 10000 + iM * 100 + day


def __date_to_quarter(dt):
    if isinstance(dt, int):
        if dt > 0 and dt < 13:
            return ((dt - 1) // 3) + 1
        y = int(dt // 10000)
        m = int(dt // 100 - y * 100)
        return ((m - 1) // 3) + 1
    return ((dt.month - 1) // 3) + 1


def __date_to_string(dt, fmt='%Y%m%d'):
    if isinstance(dt, int):
        return str(dt)
    if isinstance(dt, str):
        return dt
    return dt.strftime(fmt)


def __integer_to_date(dt):
    y, m, d = __from_date_integer(dt)
    return datetime.datetime(y, m, d)


def __date_to_integer(dt):
    if isinstance(dt, int):
        return dt
    if isinstance(dt, str):
        if '-' in dt:
            return int(dt.replace('-', ''))
        else:
            return int(dt)
    if isinstance(dt, datetime.datetime):
        d = dt.date()
        return __to_date_integer(d.year, d.month, d.day)
    if isinstance(dt, datetime.date):
        return __to_date_integer(dt.year, dt.month, dt.day)


# #
# @brief:  任意类型日期转换为 datetime
#
# @param:  dt 日期
#
# @return:  datetime.datetime

def to_datetime(dt):
    if dt is None:
        return datetime.datetime.now()
    elif isinstance(dt, str):
        if '-' in dt:
            return datetime.datetime.strptime(dt, "%Y-%m-%d")
        else:
            return datetime.datetime.strptime(dt, "%Y%m%d")
    elif isinstance(dt, int):
        sz = len(str(dt))
        if sz == 8:  # 整型日期 YYMMDD
            return __integer_to_date(dt)
        elif sz == 17:  # 整型毫秒时间 YYMMDDHHMMSSmmm
            date = (dt // 1000000000)
            ms = dt - (dt // 1000) * 1000
            tm = (dt - date * 1000000000) // 1000
            y, m, d = __from_date_integer(date)
            h, M, s = __from_time_integer(tm)
            return datetime.datetime(y, m, s, h, M, s, ms * 1000)
        elif sz > 11:  # 毫秒时间戳
            tms = time.localtime(dt / 1000)
            return datetime.datetime(tms.tm_year, tms.tm_mon, tms.tm_mday, tms.tm_hour, tms.tm_min, tms.tm_sec, int(math.modf(dt / 1000.0)[0] * 1000 * 1000))
        else:  # 秒时间戳
            tms = time.localtime(dt * 1.0)
            return datetime.datetime(tms.tm_year, tms.tm_mon, tms.tm_mday, tms.tm_hour, tms.tm_min, tms.tm_sec)
        return __integer_to_date(dt)
    elif isinstance(dt, float):
        tms = time.localtime(dt)
        return datetime.datetime(tms.tm_year, tms.tm_mon, tms.tm_mday, tms.tm_hour, tms.tm_min, tms.tm_sec)
    elif isinstance(dt, datetime.date):
        return datetime.datetime(dt.year, dt.month, dt.day)
    elif isinstance(dt, datetime.datetime):
        return dt
    else:
        raise Exception("Unsupported parameter type !", dt)


# 毫秒时间戳转datetime

def ms_to_datetime(t):
    return datetime.datetime.fromtimestamp(t / 1000.0)


# 整型日期戳转datetime

def int_to_datetime(dt):
    return __integer_to_date(dt)


# #
# @return:  int

def to_date_int(dt):
    if dt is None:
        return 0
    elif isinstance(dt, str):
        return int(dt.strip().replace('-', ''))
    elif isinstance(dt, int):
        if len(str(dt)) == 8:
            return dt
        else:
            return to_date_int(to_datetime(dt))
    elif isinstance(dt, datetime.datetime):
        return __date_to_integer(dt)
    else:
        return to_date_int(to_datetime(dt))


# 取上一天
def prev_date_int(dt):
    return to_date_int(to_datetime(dt) - datetime.timedelta(days=1))


def date_int_to_timestamp_ms(dt):
    dm = to_datetime(dt)
    ans_time = time.mktime(dm.timetuple())
    return int(ans_time * 1000)


def date_now():
    now = datetime.datetime.now()
    d = now.date()
    return __to_date_integer(d.year, d.month, d.day)


class ProgressTimer:
    def __init__(self):
        self.begin = time.time()

    def start(self):
        self.begin = time.time()

    def elapse(self):
        return int((time.time() - self.begin) * 1000)


if __name__ == '__main__':
    """
    任意日期类型转整型日期 YYMMDD
    """
    now = datetime.datetime.now()
    dt = to_date_int(now)
    print(dt, type(dt))

    dt = to_date_int('20190107')
    print(dt, type(dt))

    dt = to_date_int(20190107)
    print(dt, type(dt))

    dt = to_date_int('2019-01-07')
    print(dt, type(dt))

    # 时间戳 秒
    dt = to_date_int(1546821067)
    print(dt, type(dt))

    # 时间戳 
    dt = to_date_int(1546821067.342)
    print(dt, type(dt))

    # 时间戳 毫秒
    dt = to_date_int(1546821067342)
    print(dt, type(dt))

    """
    任意类型日期转 datetime.datetime
    """
    dt = to_datetime(now)
    print(dt, type(dt))

    dt = to_datetime('20190107')
    print(dt, type(dt))

    dt = to_datetime(20190107)
    print(dt, type(dt))

    dt = to_datetime('2019-01-07')
    print(dt, type(dt))

    dt = to_datetime(1546821067)
    print(dt, type(dt))

    dt = to_datetime(1546821067.342)
    print(dt, type(dt))

    dt = to_datetime(1546821067342)
    print(dt, type(dt))

    dt = to_datetime(dt.date())
    print(dt, type(dt))

    dt = to_datetime(20190107083107342)
    print(dt, type(dt))

    dt = to_datetime(dt.date())
    print(dt, type(dt))
    pass
