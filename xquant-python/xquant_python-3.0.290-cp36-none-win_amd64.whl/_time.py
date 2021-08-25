#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, super, range, zip, round, pow, object)

import time

from .lib import *


class EtaTime:
    __slots__ = '__time'

    def __init__(self, datetime):
        if isinstance(datetime, time.struct_time):
            self.__time = datetime
        elif 19000000 < datetime < 30000000:
            self.__time = time.strptime(str(datetime), '%Y%m%d')
        elif datetime < 100000000000:
            self.__time = time.localtime(datetime)
        else:
            self.__time = time.localtime(datetime / 1000.0)

    def __getitem__(self, item):
        if isinstance(item, str):
            return time.strftime(item, self.__time)
        else:
            return EtaTime(item)

    def to_origin_time(self):
        return self.__time

    @property
    def year(self):
        return self.__time.tm_year

    @property
    def month(self):
        return self.__time.tm_mon

    @property
    def day(self):
        return self.__time.tm_mday

    @property
    def hour(self):
        return self.__time.tm_hour

    @property
    def minute(self):
        return self.__time.tm_min

    @property
    def second(self):
        return self.__time.tm_sec

    @property
    def week(self):
        return time.strftime("%W", self.__time)

    @property
    def weekday(self):
        return self.__time.tm_wday

    @property
    def date(self):
        return int(time.strftime("%Y%m%d", self.__time))
    
    @property
    def timestamp(self):
        return time.mktime(self.__time) * 1000

    def __repr__(self):
        return 'EtaTime(year={} ,month={}, day={}, week={}, weekday={}, hour={}, minute={}, second={}, date={})' \
            .format(self.year, self.month, self.day, self.week, self.weekday, self.hour, self.minute, self.second,
                    self.date)
