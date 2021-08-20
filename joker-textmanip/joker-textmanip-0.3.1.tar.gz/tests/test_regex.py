#!/usr/bin/env python3
# coding: utf-8
import random
import re

from joker.textmanip.regex import make_range_pattern


def _reg(m, n):
    tup = tuple(sorted([m, n]))
    s = '[' + make_range_pattern([tup]) + ']'
    return re.compile(s)


def test():
    for _ in range(100):
        _reg(random.randrange(0xFF), random.randrange(0xFF))
    for _ in range(100):
        _reg(random.randrange(0xFFF), random.randrange(0xFFF))
    for _ in range(100):
        _reg(random.randrange(0xFFFF), random.randrange(0xFFFF))
