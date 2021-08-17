# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

# Python 2 and 3: forward-compatible
from past.builtins import basestring

from .constants import (
    BOOL, UINT8, INT8, UINT16, INT16, UINT32, INT32, UINT64, INT64,
    FLOAT32, FLOAT64, STRING, CHAR, BYTE, TIME, DURATION, HEADER,
    ROS_BUILTIN_TYPES, ROS_PRIMITIVE_TYPES, ROS_NUMBER_TYPES, ROS_INT_TYPES,
    ROS_FLOAT_TYPES, ROS_STRING_TYPES, ROS_BOOLEAN_TYPES, UINT8_COMPATIBLE,
    UINT16_COMPATIBLE, UINT32_COMPATIBLE, UINT64_COMPATIBLE, INT8_COMPATIBLE,
    INT16_COMPATIBLE, INT32_COMPATIBLE, INT64_COMPATIBLE, FLOAT32_COMPATIBLE,
    FLOAT64_COMPATIBLE
)
from .tokens import TypeToken

###############################################################################
# Type Checking
###############################################################################

def compatible_types(expected_type, type_token):
    assert isinstance(expected_type, TypeToken)
    assert isinstance(type_token, TypeToken)
    if expected_type is UINT8 or expected_type is CHAR:
        return type_token in UINT8_COMPATIBLE
    if expected_type is UINT16:
        return type_token in UINT16_COMPATIBLE
    if expected_type is UINT32:
        return type_token in UINT32_COMPATIBLE
    if expected_type is UINT64:
        return type_token in UINT64_COMPATIBLE
    if expected_type is INT8 or expected_type is BYTE:
        return type_token in INT8_COMPATIBLE
    if expected_type is INT16:
        return type_token in INT16_COMPATIBLE
    if expected_type is INT32:
        return type_token in INT32_COMPATIBLE
    if expected_type is INT64:
        return type_token in INT64_COMPATIBLE
    if expected_type is FLOAT32:
        return type_token in FLOAT32_COMPATIBLE
    if expected_type is FLOAT64:
        return type_token in FLOAT64_COMPATIBLE
    return expected_type == type_token

def possible_types(value):
    if isinstance(value, basestring):
        return STRING
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, float):
        return tuple(ros_type for ros_type in ROS_FLOAT_TYPES
            if value >= ros_type.min_value and value <= ros_type.max_value)
    assert isinstance(value, (int, long))
    return tuple(ros_type for ros_type in ROS_NUMBER_TYPES
        if value >= ros_type.min_value and value <= ros_type.max_value)
