# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals
from builtins import range # Python 2 and 3: forward-compatible
import importlib

from .constants import (HEADER, ROS_BUILTIN_TYPES)
from .tokens import (ArrayType, MessageType)
from .values import (RosBool, RosFloat, RosInt, RosString)

# lazy imports of msg packages given as arguments
# lazy import of genmsg


###############################################################################
# Type System
###############################################################################

_cache = {t.type_name: t for t in ROS_BUILTIN_TYPES}
_cache["Header"] = HEADER

def clear_cache():
    global _cache
    _cache = {t.type_name: t for t in ROS_BUILTIN_TYPES}
    _cache["Header"] = HEADER

def get_type(type_name):
    global _cache
    try:
        return _cache[type_name]
    except KeyError as ke:
        if "/" not in type_name:
            raise ValueError("Invalid message type name: {}".format(type_name))
        try:
            msg_class = _load_msg_class(type_name)
            fields = _get_class_fields(msg_class)
            constants = _get_class_constants(msg_class)
            type_token = MessageType(type_name, fields, constants=constants)
            _cache[type_name] = type_token
            return type_token
        except ImportError as ie:
            raise KeyError("Cannot import message {}".format(type_name))

def _load_msg_class(type_name):
    pkg, msg = type_name.split("/")
    module = importlib.import_module(pkg + ".msg")
    msg_class = getattr(module, msg)
    return msg_class

def _get_class_fields(msg_class):
    from genmsg.msgs import parse_type
    fields = {}
    for i in range(len(msg_class.__slots__)):
        field_name = msg_class.__slots__[i]
        field_type = msg_class._slot_types[i]
        base_type, is_array, length = parse_type(field_type)
        type_token = get_type(base_type)
        if is_array:
            type_token = ArrayType(type_token, length=length)
        fields[field_name] = type_token
    return fields

def _get_class_constants(msg_class):
    from genmsg.base import InvalidMsgSpec
    from genmsg.msg_loader import _load_constant_line, _strip_comments
    constants = {}
    lines = msg_class._full_text.splitlines()
    for line in lines:
        clean_line = _strip_comments(line)
        if not clean_line or not "=" in clean_line:
            continue # ignore empty/field lines
        try:
            constant = _load_constant_line(line)
            constants[constant.name] = _make_literal(
                constant.val, get_type(constant.type))
        except InvalidMsgSpec as e:
            pass
    return constants

def _make_literal(value, type_token):
    assert type_token.is_primitive
    if type_token.is_int:
        return RosInt(value, type_token)
    if type_token.is_float:
        return RosFloat(value, type_token)
    if type_token.is_bool:
        return RosBool(value)
    assert type_token.is_string
    return RosString(value)
