#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
"""
日期时间工具类
"""


class DateUtils(object):

    @staticmethod
    def get_first_last_by_month(year=None, month=None, format_str='%Y-%m-%d %H:%M:%S'):
        """
            根据年份，月份获取当月第一天和当月最后一天
        """
        year, month, day = DateUtils._check_null(year, month)
        this_mouth_first = datetime.datetime(year, month, 1, 0, 0, 0)
        future_mouth_first = DateUtils.get_future_mouth_first(year, month)
        this_mouth_last = future_mouth_first - datetime.timedelta(days=1)
        return this_mouth_first.strftime(format_str), this_mouth_last.strftime(format_str)

    @staticmethod
    def get_first_last_by_day(year=None, month=None, day=None, format_str='%Y-%m-%d %H:%M:%S'):
        """
        根据年份和月份和日，获取指定日期的第一秒钟和最后一秒钟
        """
        year, month, day = DateUtils._check_null(year, month, day)
        this_day_first = datetime.datetime(year, month, day, 0, 0, 0)
        this_day_last = datetime.datetime(year, month, day, 23, 59, 59)
        return this_day_first.strftime(format_str), this_day_last.strftime(format_str)

    @staticmethod
    def get_future_mouth_first(year, month):
        """
        获取下个月第一天
        """
        if month == 12:
            month = 0
            year = year + 1
        future_mouth_first = datetime.datetime(year, month + 1, 1, 0, 0, 0)
        return future_mouth_first

    @staticmethod
    def _check_null(year=None, month=None, day=None):
        """
        监测年月日，默认为今天
        """
        now_time = datetime.datetime.now()
        if year is None:
            year = now_time.year
        if month is None:
            month = now_time.month
        if day is None:
            day = now_time.day
        return year, month, day

    @staticmethod
    def get_timestamp():
        """
        获取当前时间戳
        """
        t = time.time()
        return int(round(t * 1000))

    @staticmethod
    def now(t: datetime = None, format_str='%Y-%m-%d %H:%M:%S'):
        """
        获取格式化时间撮当前时间
        """
        if t is None:
            t = datetime.datetime.now()
        return t.strftime(format_str)


if __name__ == '__main__':
    pass
