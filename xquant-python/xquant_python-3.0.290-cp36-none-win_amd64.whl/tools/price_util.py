#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function

__PRICE_EPSILON = 0.000001


def equal(x, y, epsilon=__PRICE_EPSILON):
    return abs(x - y) < epsilon


def greater_than(x, y):
    return x - y > __PRICE_EPSILON


def less_than(x, y):
    return y - x > __PRICE_EPSILON


def equal_greater_than(x, y):
    return equal(x, y) or greater_than(x, y)


def equal_less_than(x, y):
    return equal(x, y) or less_than(x, y)


def compare(x, y):
    if equal(x, y):
        return 0
    elif greater_than(x, y):
        return 1
    else:
        return -1


def valid_price(price):
    return greater_than(price, 0)


def is_zero(x):
    return equal(x, 0)


def same_side(x, y):
    return ((equal_greater_than(x, 0) and equal_greater_than(y, 0)) or
            (equal_less_than(x, 0) and equal_less_than(y, 0))
            )
