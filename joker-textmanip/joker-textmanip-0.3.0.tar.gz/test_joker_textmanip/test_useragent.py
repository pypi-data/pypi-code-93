#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import os
import sys

from joker.textmanip.useragent import UserAgent


def loc(filename):
    p = os.path.realpath(__file__)
    p = os.path.abspath(p)
    d, f = os.path.split(p)
    return os.path.join(d, filename)


def test_useragent():
    strings = open(loc('useragents.txt'))
    for s in strings:
        s = s.strip()
        if not s.strip():
            continue
        print(repr(UserAgent.from_string(s)), file=sys.stderr)


if __name__ == '__main__':
    test_useragent()
