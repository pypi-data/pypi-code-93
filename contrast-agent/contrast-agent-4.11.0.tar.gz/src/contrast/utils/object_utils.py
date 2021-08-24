# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import copy
from inspect import isclass


def safe_copy(value):
    """
    Return a safe copy of a value

    :param value: to be copied
    :return: copied value if no exception
    """
    try:
        return copy.copy(value)
    except:
        return value


def get_name(obj):
    return "{0.__module__}.{0.__name__}".format(obj) if isclass(obj) else obj.__name__
