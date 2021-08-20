# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-03-08 17:56:43
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2020-03-08 17:57:35

import datetime
import json as _json

# Date ISO formats
ISO8601_10_DIGITS = "%Y-%m-%d"

ISO8601_17_DIGITS = "%Y-%m-%dT%H%M%S"
ISO8601_17_DIGITS_V2 = "%Y-%m-%d %H%M%S"

ISO8601_19_DIGITS = "%Y-%m-%dT%H:%M:%S"
ISO8601_19_DIGITS_V2 = "%Y-%m-%d %H:%M:%S"

ISO8601_20_DIGITS = "%Y-%m-%dT%H:%M:%SZ"
ISO8601_20_DIGITS_V2 = "%Y-%m-%d %H:%M:%SZ"

# Different JSON parsers have got different ParseError objects.
JsonParseError = ValueError

# Default-Parameters for the *dumps*-function
dumps_skipkeys = False
dumps_ensure_ascii = True
dumps_check_circular = True
dumps_allow_nan = True
dumps_cls = None
dumps_indent = None
dumps_separators = None
dumps_encoding = "utf-8"
dumps_default = None
dumps_sort_keys = False

# Default-Parameters for the *loads*-function
loads_encoding = None
loads_cls = None
loads_object_hook = None
loads_parse_float = None
loads_parse_int = None
loads_parse_constant = None
loads_object_pairs_hook = None

def soa_loads(data_struct):
    def my_json_obj_hook(data):
        def check_json(input_str):
            try:
                _json.loads(input_str)
                return True
            except:
                return False

        for key,values in data.items():
            if check_json(values):
                data[key] = _json.loads(values)
        return data
    return _json.loads(data_struct, object_hook=my_json_obj_hook)