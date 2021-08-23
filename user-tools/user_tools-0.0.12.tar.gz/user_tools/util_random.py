#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_random.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Custom random function."""
import random


def random_str(string: str) -> str:
    """Randomly shuffle strings."""
    list_str = list(string)
    random.shuffle(list_str)
    return "".join(list_str)


if __name__ == "__main__":
    pass
