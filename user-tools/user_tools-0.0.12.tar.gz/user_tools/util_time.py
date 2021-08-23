#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_time.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Some functions related to time operations."""
import time

NOW_TIME = time.time()


def format_time(timestamp: float = NOW_TIME,
                format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format timestamp returns format_str time.

    :param timestamp(float): The timestamp to be formatted.\n
        Defaults is the current timestamp.\n
    :param format_str(str): Time format used to format time.\n
        Default is '%Y-%m-%d %H:%M:%S'.\n
        Commonly used format codes:\n
            %Y: Year with century as a decimal number.\n
            %m: Month as a decimal number [01,12].\n
            %d: Day of the month as a decimal number [01,31].\n
            %H: Hour (24-hour clock) as a decimal number [00,23].\n
            %M: Minute as a decimal number [00,59].\n
            %S: Second as a decimal number [00,61].\n
            %z: Time zone offset from UTC.\n
            %a: Locale's abbreviated weekday name.\n
            %A: Locale's full weekday name.\n
            %b: Locale's abbreviated month name.\n
            %B: Locale's full month name.\n
            %c: Locale's appropriate date and time representation.\n
            %I: Hour (12-hour clock) as a decimal number [01,12].\n
            %p: Locale's equivalent of either AM or PM.\n
    :return(str): Formatted time string."""

    tmp_time = time.localtime(timestamp)
    return time.strftime(format_str, tmp_time)


if __name__ == "__main__":
    pass
