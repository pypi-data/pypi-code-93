#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_cmd.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Some functions related to command execution."""
import subprocess
import platform
from typing import Any, Dict, List


def get_out_text(cmd: List[str], encoding: str = "") -> Dict[str, Any]:
    """Run command with arguments and return its output.

    :param cmd(list): Command to be executed.\n
        The command format is ["command", ["arg", "arg1",...]]\n
    :return(dict): Command execution results of cmd."""
    if not encoding:
        if "win" in platform.system().lower():
            encoding = "gbk"
        else:
            encoding = "UTF-8"
    code = 0
    try:
        out_bytes = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
    if code:
        out_text = {
            "err_code": str(code),
            "output_text": out_bytes.decode(encoding)
        }
    else:
        out_text = {
            "err_code": '',
            "output_text": out_bytes.decode(encoding)
        }
    return out_text


if __name__ == "__main__":
    pass
