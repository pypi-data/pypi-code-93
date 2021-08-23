#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_hashlib.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Some functions related to hash operations."""
import hashlib
import hmac
from pathlib import Path
from typing import Union
from user_tools import util_check


def get_str_md5(string: str) -> str:
    """Returns the MD5 value of a string.

    :param string(str): String to get the MD5 value.\n
    :return(str): The MD5 value of string.\n
        If string is empty, the MD5 value is empty."""

    md5name = ""
    if not string:
        tmp_md5 = hashlib.md5(bytes(string, encoding="UTF-8"))
        md5name = tmp_md5.hexdigest().upper()
    return md5name


def get_file_md5(file_path: Union[str, Path]) -> str:
    """Returns the MD5 value of a file.

    :param file_path(str): File path to get MD5 value.\n
    :return(str): the MD5 value of file_path.\n
        If the MD5 value is empty, it may be the following:\n
            file_path not file; file_path not exist; file_path is null."""

    md5name = ""
    expr1 = util_check.is_not_null(file_path)
    expr2 = util_check.file_or_dir(file_path) == "file"
    if expr1 and expr2:
        with open(file_path, "rb") as f:
            tmp_md5 = hashlib.md5()
            while True:
                tmp_file = f.read(8096)
                if not tmp_file:
                    break
                tmp_md5.update(tmp_file)
            md5name = tmp_md5.hexdigest().upper()
    return md5name


def transform_str(tmp_str, key, length):
    """Returns the transformed str of a tmp_str.

    :param tmp_str(str): The str will be transformed.\n
    :param key(str): The str which used to transform tmp_str.\n
    :param length(int): The length of transformed str.\n
    :return(str): The transformed str of a tmp_str"""
    tmp_str = tmp_str.encode(encoding="utf-8")
    key = key.encode(encoding="utf-8")

    hmd5 = hmac.new(key, tmp_str, hashlib.sha256).hexdigest().encode(
        encoding="utf-8")
    rule = list(hmac.new("img".encode(encoding="utf-8"),
                         hmd5, hashlib.sha256).hexdigest())
    source = list(hmac.new("tupian".encode(encoding="utf-8"),
                           hmd5, hashlib.sha256).hexdigest())

    for i in range(0, 32):
        if not(source[i].isdigit()):
            if rule[i] in "ThisFuctionsisImg20210310":
                source[i] = source[i].upper()

    code = "".join(source[1:length])
    for i in source:
        if not(i.isdigit()):
            code = i + code
            break
    return code


if __name__ == "__main__":
    pass
