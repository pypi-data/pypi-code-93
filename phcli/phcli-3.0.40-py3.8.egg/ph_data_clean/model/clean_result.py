# -*- coding: utf-8 -*-

import json
from enum import Enum


class Tag(Enum):
    SUCCESS = 1
    EMPTY_DICT = 0
    MISSING_COL = -1
    WARNING = 2
    PH_ERR = -9999
    UNDEFINED = -888


class CleanResult(object):
    """
    清洗结果
    """

    def __init__(self, data, metadata, raw_data, tag, err_msg = ''):
        self.data = data
        self.metadata = metadata
        self.raw_data = raw_data
        self.tag = tag
        self.err_msg = err_msg

    def __str__(self):
        result = {
            "data": self.data,
            "metadata": self.metadata,
            "raw_data": self.raw_data,
            "tag": self.tag.value,
            "errMsg": self.err_msg
        }
        return json.dumps(result, ensure_ascii=False)
