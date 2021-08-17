# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

# Python 2 and 3: forward-compatible
from __future__ import unicode_literals
from builtins import str
from collections import namedtuple

from .tokens import TypeToken


###############################################################################
# Builtin Type Tokens
###############################################################################

_TOKEN_PROPERTIES = ("type_name", "is_builtin", "is_primitive", "is_number",
                     "is_int", "is_float", "is_bool", "is_string", "is_time",
                     "is_duration", "is_header", "is_message", "is_array")
BuiltinPlainTypeToken = namedtuple("BuiltinPlainTypeToken", _TOKEN_PROPERTIES)
BuiltinPlainTypeToken.__bases__ = (TypeToken,) + BuiltinPlainTypeToken.__bases__

_NUM_PROPERTIES = _TOKEN_PROPERTIES + ("min_value", "max_value")
BuiltinNumTypeToken = namedtuple("BuiltinNumTypeToken", _NUM_PROPERTIES)
BuiltinNumTypeToken.__bases__ = (TypeToken,) + BuiltinNumTypeToken.__bases__

_MSG_PROPERTIES = _TOKEN_PROPERTIES + ("fields", "constants")
BuiltinMsgTypeToken = namedtuple("BuiltinMsgTypeToken", _MSG_PROPERTIES)
BuiltinMsgTypeToken.__bases__ = (TypeToken,) + BuiltinMsgTypeToken.__bases__


BOOL = BuiltinNumTypeToken(
    "bool",         # type_name
    True,           # is_builtin
    True,           # is_primitive
    False,          # is_number
    False,          # is_int
    False,          # is_float
    True,           # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    0,              # min_value
    1               # max_value
)

UINT8 = BuiltinNumTypeToken(
    "uint8",        # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    0,              # min_value
    (2 ** 8) - 1    # max_value
)

CHAR = UINT8

UINT16 = BuiltinNumTypeToken(
    "uint16",       # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    0,              # min_value
    (2 ** 16) - 1   # max_value
)

UINT32 = BuiltinNumTypeToken(
    "uint32",       # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    0,              # min_value
    (2 ** 32) - 1   # max_value
)

UINT64 = BuiltinNumTypeToken(
    "uint64",       # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    0,              # min_value
    (2 ** 64) - 1   # max_value
)

INT8 = BuiltinNumTypeToken(
    "int8",         # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    -(2 ** 7),      # min_value
    (2 ** 7) - 1    # max_value
)

BYTE = INT8

INT16 = BuiltinNumTypeToken(
    "int16",        # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    -(2 ** 15),     # min_value
    (2 ** 15) - 1   # max_value
)

INT32 = BuiltinNumTypeToken(
    "int32",        # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    -(2 ** 31),     # min_value
    (2 ** 31) - 1   # max_value
)

INT64 = BuiltinNumTypeToken(
    "int64",        # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    True,           # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    -(2 ** 63),     # min_value
    (2 ** 63) - 1   # max_value
)

FLOAT32 = BuiltinNumTypeToken(
    "float32",      # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    False,          # is_int
    True,           # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    -3.3999999521443642e+38, # min_value
    3.3999999521443642e+38   # max_value
)

FLOAT64 = BuiltinNumTypeToken(
    "float64",      # type_name
    True,           # is_builtin
    True,           # is_primitive
    True,           # is_number
    False,          # is_int
    True,           # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False,          # is_array
    -1.7E+308,      # min_value
    1.7E+308        # max_value
)

STRING = BuiltinPlainTypeToken(
    "string",       # type_name
    True,           # is_builtin
    True,           # is_primitive
    False,          # is_number
    False,          # is_int
    False,          # is_float
    False,          # is_bool
    True,           # is_string
    False,          # is_time
    False,          # is_duration
    False,          # is_header
    False,          # is_message
    False           # is_array
)

TIME = BuiltinMsgTypeToken(
    "time",         # type_name
    True,           # is_builtin
    False,          # is_primitive
    False,          # is_number
    False,          # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    True,           # is_time
    False,          # is_duration
    False,          # is_header
    True,           # is_message
    False,          # is_array
    {               # fields
        "secs": UINT32,
        "nsecs": UINT32
    },
    {}              # constants
)

DURATION = BuiltinMsgTypeToken(
    "duration",     # type_name
    True,           # is_builtin
    False,          # is_primitive
    False,          # is_number
    False,          # is_int
    False,          # is_float
    False,          # is_bool
    False,          # is_string
    False,          # is_time
    True,           # is_duration
    False,          # is_header
    True,           # is_message
    False,          # is_array
    {               # fields
        "secs": INT32,
        "nsecs": INT32
    },
    {}              # constants
)

HEADER = BuiltinMsgTypeToken(
    "std_msgs/Header",  # type_name
    True,               # is_builtin
    False,              # is_primitive
    False,              # is_number
    False,              # is_int
    False,              # is_float
    False,              # is_bool
    False,              # is_string
    False,              # is_time
    False,              # is_duration
    True,               # is_header
    True,               # is_message
    False,              # is_array
    {                   # fields
        "seq": UINT32,
        "stamp": TIME,
        "frame_id": STRING
    },
    {}                  # constants
)
