#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_file.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Some functions related to file operations."""
import os
from pathlib import Path
from typing import Any, Union
from user_tools import util_time, util_check

SIZE_UNIT = {
    "GB": float(1024*1024*1024),
    "MB": float(1024*1024),
    "KB": float(1024)
}


def write_file(file_path: Union[str, Path],
               msg: str, mode: str = "a", encoding: str = "UTF-8") -> None:
    """Write the contents of msg to file_path.

    :param file_path(str): File to be written.\n
    :param msg(str): What will be written to the file_path.\n
    :param mode(str): How to write file, default is "a".\n
        Character Meaning\n
            'w'   open for writing, create if not exists.
                  truncating the file first.\n
            'x'   create a new file and open it for writing\n
            'a'   open for writing, create if not exists.
                  appending to the end of the file (default).\n
            'b'   binary mode.
                  If you use this, no encoding parameter is required\n
            't'   text mode (default).
            '+'   open a disk file for updating (reading and writing)\n
    :param encoding(str): Encoding format to write file, default is "UTF-8".\n
    :return(None): No return value."""

    if "b" not in mode:
        with open(file_path, mode, encoding=encoding) as f:
            f.write(msg)
    else:
        with open(file_path, mode) as f:
            f.write(msg)


def read_file(file_path: Union[str, Path], need_list: bool = False,
              mode: str = "r", encoding: str = "UTF-8") -> Any:
    """Return the content of file_path.

    :param file_path(str): File to be read.\n
    :param mode(str): How to read file, default is "r".\n
        Character Meaning\n
            'r'   open for reading (default).\n
            'b'   binary mode.
                  If you use this, no encoding parameter is required\n
            't'   text mode (default).\n
    :param encoding(str): Encoding format to read file, default is "UTF-8".\n
    :return(str): The contents of file_path.\n
        If the contents of file_path is empty, it may be the following:\n
            file_path not file; file_path not exist; file_path is null."""

    msg = ""
    expr1 = util_check.is_not_null(file_path)
    expr2 = util_check.file_or_dir(file_path) == "file"
    if expr1 and expr2:
        if "b" not in mode:
            with open(file_path, mode, encoding=encoding) as f:
                if need_list:
                    msg = []
                    lines = f.readlines()
                    for line in lines:
                        msg.append(line.strip())
                else:
                    msg = f.read()
        else:
            with open(file_path, mode) as f:
                msg = f.read()
    return msg


def get_file_suffix(filename: str) -> str:
    """Return the suffix of filename.

    :param filename(str): File name to get the suffix.\n
    :return(str): The suffix of filename."""

    return Path(filename).suffix


def get_file_size(file_path: Union[str, Path],
                  size_unit: str = "MB") -> float:
    """Return the size of file_path.

    :param file_path(str): File path to get file size.\n
    :param size_unit(str): File size unit. Default is 'MB'.\n
        Character Meaning\n
        'GB': The file's byte size will be divided by 1024*1024*1024\n
        'MB': The file's byte size will be divided by 1024*1024\n
        'KB': The file's byte size will be divided by 1024\n
    :return(float): The size of file_path.\n
        Exact to two digits after the decimal point.\n
        A file size of -1 means the file does not exist."""

    size_type = 0.0
    if size_unit in SIZE_UNIT:
        size_type = SIZE_UNIT[size_unit]
    else:
        size_type = SIZE_UNIT["MB"]
    file_size = -1.0
    if util_check.is_exist(file_path):
        tmp_size = os.path.getsize(file_path)
        size = tmp_size / size_type
        file_size = round(size, 2)
    return file_size


def get_file_ctime(file_path: Union[str, Path],
                   format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Get and format file creation time and return.

    :param file_path(str): File path to get creation time.\n
    :param format_str(str): Time format used to format time.\n
        Default is '%Y-%m-%d %H:%M:%S'\n
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
    :return(str): A formatted time string of file_path creation time.\n
        If the creation time is an empty string, the file does not exist."""

    ctime = ""
    if util_check.is_exist(file_path):
        tmp_time = os.path.getctime(file_path)
        ctime = util_time.format_time(tmp_time, format_str)
    return ctime


def get_file_atime(file_path: Union[str, Path],
                   format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Get and format file access time and return.

    :param file_path(str): File path to get access time.\n
    :param format_str(str): Time format used to format time.\n
        Default is '%Y-%m-%d %H:%M:%S'\n
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
    :return(str): A formatted time string of file_path access time.\n
        If the access time is an empty string, the file does not exist."""

    atime = ""
    if util_check.is_exist(file_path):
        tmp_time = os.path.getatime(file_path)
        atime = util_time.format_time(tmp_time, format_str)
    return atime


def get_file_mtime(file_path: Union[str, Path],
                   format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Get and format file modification time and return.

    :param file_path(str): File path to get modification time.\n
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
    :return(str): A formatted time string of file_path modification time.\n
        If the modification time is an empty string,\n
        the file does not exist."""

    mtime = ""
    if util_check.is_exist(file_path):
        tmp_time = os.path.getmtime(file_path)
        mtime = util_time.format_time(tmp_time, format_str)
    return mtime


if __name__ == "__main__":
    pass
