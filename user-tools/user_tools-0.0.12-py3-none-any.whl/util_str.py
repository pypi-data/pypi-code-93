#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_str.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Custom str function."""


def format_str(string: str) -> str:
    r"""Remove all kinds of blanks in the string,
       including full-width blanks and non-breaking blanks.

       The list is \r\n, \t, \r, \n, \xa0, \u3000, &nbsp;, [space]"""
    string = string.replace("\r\n", "")
    string = string.replace("\t", "")
    string = string.replace("\r", "")
    string = string.replace("\n", "")
    string = string.replace("\xa0", "")
    string = string.replace("\u3000", "")
    string = string.replace("&nbsp;", "")
    string = string.strip()
    return string


if __name__ == "__main__":
    pass
