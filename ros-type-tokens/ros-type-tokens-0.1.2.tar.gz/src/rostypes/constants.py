# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

from .builtinros import (
    BOOL, UINT8, INT8, UINT16, INT16, UINT32, INT32, UINT64, INT64,
    FLOAT32, FLOAT64, STRING, CHAR, BYTE, TIME, DURATION, HEADER
)

###############################################################################
# Type Constants
###############################################################################

ROS_BUILTIN_TYPES = (BOOL, UINT8, INT8, UINT16, INT16, UINT32, INT32, UINT64,
                     INT64, FLOAT32, FLOAT64, STRING, CHAR, BYTE, TIME,
                     DURATION, HEADER)

ROS_PRIMITIVE_TYPES = (BOOL, UINT8, INT8, UINT16, INT16, UINT32, INT32, UINT64,
                       INT64, FLOAT32, FLOAT64, STRING, CHAR, BYTE)

ROS_NUMBER_TYPES = (UINT8, INT8, UINT16, INT16, UINT32, INT32, UINT64, INT64,
                    FLOAT32, FLOAT64, CHAR, BYTE)

ROS_INT_TYPES = (UINT8, INT8, UINT16, INT16, UINT32, INT32, UINT64, INT64,
                 CHAR, BYTE)

ROS_FLOAT_TYPES = (FLOAT32, FLOAT64)

ROS_STRING_TYPES = (STRING,)

ROS_BOOLEAN_TYPES = (BOOL,)

UINT8_COMPATIBLE = (UINT8, CHAR)
UINT16_COMPATIBLE = (UINT8, CHAR, UINT16)
UINT32_COMPATIBLE = (UINT8, CHAR, UINT16, UINT32)
UINT64_COMPATIBLE = (UINT8, CHAR, UINT16, UINT32, UINT64)
INT8_COMPATIBLE = (INT8, BYTE)
INT16_COMPATIBLE = (UINT8, CHAR, INT8, BYTE, INT16)
INT32_COMPATIBLE = (UINT8, CHAR, INT8, BYTE, UINT16, INT16, INT32)
INT64_COMPATIBLE = (UINT8, CHAR, INT8, BYTE, UINT16,
                    INT16, UINT32, INT32, INT64)
FLOAT32_COMPATIBLE = (UINT8, CHAR, INT8, BYTE, UINT16, INT16, FLOAT32)
FLOAT64_COMPATIBLE = (UINT8, INT8, UINT16, INT16, UINT32,
                      INT32, CHAR, BYTE, FLOAT32, FLOAT64)
