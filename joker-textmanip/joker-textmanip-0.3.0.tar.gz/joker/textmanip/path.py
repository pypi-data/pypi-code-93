#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import datetime
import os
import re

windows_reserved_names = {
    'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
    'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
    'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
}


def windows_filename_safe(s, repl='_'):
    # <>:"/\\|?* and ASCII 0 - 31
    # https://stackoverflow.com/a/31976060/2925169
    ordinals = [ord(c) for c in '<>:"/\\|?*']
    ordinals.extend(range(32))
    s = s.translate(dict.fromkeys(ordinals, repl))
    if s.endswith('.'):
        s = s[:-1]
    if s.upper() in windows_reserved_names:
        s += '_'
    return s


def unix_filename_safe(s):
    # ASCII 47: "/"
    return s.translate(dict.fromkeys([0, 47]))


def proper_filename(s):
    s = windows_filename_safe(s.strip(), '_')
    # replace leading .-, quotes/spaces with _
    s = re.sub(r'^-', '_', s)
    s = re.sub(r"['\s]+", '_', s)
    s = re.sub(r'\s*\(([0-9]+)\)\.', r'-\1.', s)
    return s


def make_new_path(path, ext=None, check=1):
    """
    :param path: (str)
    :param ext: (str)
    :param check: (int)
    :return: (str)

    check = -1: return a modified path
    check = 0: do not check existence
    check = 1: raise FileExistsError

    >>> make_new_path('~/html/index.txt', 'html')
    '~/html/index.html'
    >>> make_new_path('~/html/index.txt', '.html')
    '~/html/index.txt.html'
    """
    if ext is not None:
        if not ext.startswith(os.extsep):
            ext = os.extsep + ext
        path = os.path.splitext(path)[0] + ext

    if check == 0:
        return path

    while os.path.exists(path):
        if check == 1:
            raise FileExistsError(path)
        base_path, ext = os.path.splitext(path)
        a = base_path, datetime.datetime.now(), id(path) % 100, ext
        path = '{}.{:%y%m%d-%H%M%S}-{:02}{}'.format(*a)
    return path


