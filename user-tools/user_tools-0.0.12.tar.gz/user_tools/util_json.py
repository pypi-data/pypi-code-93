#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_json.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Some functions related to json file operations."""
import json
from typing import Any, Dict, Union
from pathlib import Path
from user_tools import util_check


def read_json(json_file: Union[str, Path]) -> Dict[Any, Any]:
    """Return the contents of json_file.

    :param json_file(str): Json file to be read.\n
    :return(dict): the contents of json_file.\n
        If the return value is empty, it may be the following:\n
            json_file not file; json_file not exist; json_file is null."""

    json_dict = {}
    expr1 = util_check.is_not_null(json_file)
    expr2 = util_check.file_or_dir(json_file) == "file"
    if expr1 and expr2:
        with open(json_file, "r", encoding="UTF-8") as f:
            json_dict = json.load(f)
    return json_dict


def write_json(json_file: Union[str, Path], json_dict: Dict[Any, Any],
               mode: str = "w") -> None:
    """Write the contents of json_dict to json_file.

    :param json_file(str): Json file to be written.\n
    :param json_dict(str): What will be written to the json file.\n
    :param mode(str): How to write json file, default is "w".\n
        Character Meaning\n
            'w'   open for writing, create if not exists.
                  truncating the file first.\n
            'x'   create a new file and open it for writing.\n
            'a'   open for writing, create if not exists.
                  appending to the end of the file.\n
            'b'   binary mode.
                  If you use this, no encoding parameter is required\n
            't'   text mode (default)\n
            '+'   open a disk file for updating (reading and writing)\n
    :return(None): No return value."""

    with open(json_file, mode, encoding="UTF-8") as f:
        # ensure_ascii = False is to display Chinese,
        # if not written, it will be displayed as unicode encoding.
        # indent is to format the json file,
        # otherwise it will be displayed on one line.
        json.dump(json_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    pass
