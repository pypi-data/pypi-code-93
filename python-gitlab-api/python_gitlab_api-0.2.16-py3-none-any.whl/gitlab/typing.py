"""Some typing definitions local to this package
"""
#from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

# pylint: disable=missing-function-docstring,missing-docstring
# pylint: disable=too-few-public-methods


# Python data structure represenation of JSON data
# https://www.rfc-editor.org/rfc/rfc7159.txt defines json as a sequence of
# false / null / true / object / array / number / string
JSON = Union[Dict,Tuple,List, int, float, str, bool, None]


class GitLabAPIReceivedError(Exception):
    def __init__(self, message: str, data: JSON):
        super().__init__(message, data)
        self.msg = message
        self.data = data

    def __str__(self) -> str:
        return f"REST API Error received: {self.msg}: {self.data}"
