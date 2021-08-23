#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_check.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Some checks on files or directories."""
import os
import re
from typing import Dict, List, Tuple, Union
from pathlib import Path
import threading
import socket


def is_exist(file_path: Union[str, Path], create: bool = False) -> bool:
    """Test whether file_path exists.

    :param file_path(str): The path that needs to be judged.\n
    :param create(bool): Whether to create. If create is True,\n
            create a directory named file_path if it does not exist.\n
    :return(bool): A boolean representing whether file_path exists."""

    if create and not os.path.exists(file_path):
        os.makedirs(file_path)
    return os.path.exists(file_path)


def is_not_null(file_path: Union[str, Path]) -> bool:
    """Test whether file_path is not null.

    :param file_path(str): The path that needs to be judged.\n
    :return(bool): Returns whether file_path is not null.\n
        Return True if file_path exist and not null.\n
        Return False, it may be the following:\n
            file_path not file or dir; file_path not exist."""

    result = False
    if is_exist(file_path):
        if file_or_dir(file_path) == "file":
            result = os.path.getsize(file_path) != 0
        elif file_or_dir(file_path) == "dir":
            result = bool(os.listdir(file_path))
    return result


def file_or_dir(file_path: Union[str, Path]) -> str:
    """ Returns file type of the file_path.

    :param file_path(str): The path that needs to be judged.\n
    :return(str): Returns file type of the file_path.\n
        The return values are as follows.\n
            "dir": If file_path is a directory,\n
            "file": If file_path is a file,\n
            file_path + "Not exist!": If file_path is not exist\n
            "Not file or dir!": If file_path not a dir or file."""

    result = ""
    if not is_exist(file_path):
        result = str(file_path) + "Not exist!"
    elif os.path.isdir(file_path):
        result = "dir"
    elif os.path.isfile(file_path):
        result = "file"
    else:
        result = "Not file or dir!"
    return result


def check_ip(ip: str) -> bool:
    """Test whether the IP is valid.

    :param ip(str): The IP that needs to be judged.\n
    :return(bool): Returns whether url is valid.\n
        Return False, if the IP is not legal."""

    ip_rex = r'(?=(\b|\D))(((\d{1,2})|(1\d{1,2})|(2[0-4]\d)|(25[0-5]))\.)' + \
        r'{3}((\d{1,2})|(1\d{1,2})|(2[0-4]\d)|(25[0-5]))(?=(\b|\D))'

    is_legal = re.match(re.compile(ip_rex), ip)
    if is_legal:
        return True
    else:
        return False


def check_url(url: str, style: str = "http") -> bool:
    """Test whether url is valid.

    :params url(str): The url that needs to be judged.\n
    :return(bool): Returns whether url is valid.\n
        Return False, if the style is not web or git.
    """

    result = False
    if style == "http":
        result = True if re.match(r'^https?:/{2}\w.+$', url) else False
    elif style == "git":
        result = True if re.match(
            r'^(http(s)?:\/\/([^\/]+?\/){2}|git@[^:]+:[^\/]+?\/).*?.git$', url
        ) else False
    return result


def check_arg(info_dict: Dict, required_list: List, empty_arg: List,
              optional_list: List, method="") -> Tuple:
    """Check whether the parameters are correct.

    :param info_dict(Dict): Information about whether the parameter
                            being checked is correct.
    :param required_list(List): List of required parameters.
    :param optional_list(List): List of Optional parameters.
    :param empty_arg(List): List of nullable parameters.
    :param method(str): Method of checking parameters.
        one: Info_dict must contains at least one parameter from optional_list.

    :return Tuple(bool, Any): If there is no error, return (True, ""),
        otherwise False and an error message is returned."""

    flag = False

    # Check if parameter in info_dict not exists
    # in required_list, optional_list and empty_arg.
    not_exist = []
    for i in info_dict.keys():
        if i not in required_list and i not in optional_list and\
                i not in empty_arg:
            not_exist.append(i)
            flag = True
    if flag:
        return (False, "Please confirm whether the following parameters\
                        are correct: " + ",".join(not_exist))

    # Check if parameter in required_list not exists in info_dict.
    for _ in required_list:
        if _ not in info_dict:
            return (False, f"{' '.join(required_list)} \
                             are all required parameter")

    # Check if parameter in required_list is not null.
    for k, v in info_dict.items():
        if not v and k not in empty_arg:
            return (False, f"The parameter {k}'value cannot be empty")

    flag = True
    if method == "one":
        for _ in optional_list:
            if _ in info_dict:
                flag = False
        if flag:
            return (False, f"Info_dict must contains at least one parameter\
                             from optional_list")

    # Check if the format of parameter in info_dict is correct.
    return (True, "")


def check_port(IP, Port, protocol="tcp", timeout=1):
    """Check whether the Port on IP is open.

    :param IP(str): The IP that needs to be checked.\n
    :param Port(int): The Port on IP that needs to be checked.\n
    :param timeout(int): Timeout period.

    :return Tuple(bool, Any): If there is no error, return (True, ""),
        otherwise False and an error message is returned."""

    threadlock = threading.Lock()
    flag = False
    result = ""
    socket.setdefaulttimeout(timeout)
    try:
        if protocol.lower() == "tcp":
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif protocol.lower() == "udp":
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            return (False, "The protocol only can be TCP or UDP")
        conn.connect((IP, Port))
        threadlock.acquire()
        flag = True
    except Exception as e:
        threadlock.acquire()
        result = str(e)
    finally:
        threadlock.release()
        conn.close()
        return (flag, result)


if __name__ == "__main__":
    pass
