# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

# Python 2 and 3: forward-compatible
from __future__ import unicode_literals
from builtins import object, str
from past.builtins import basestring

from .constants import (BOOL, ROS_FLOAT_TYPES, ROS_INT_TYPES, STRING)

if not hasattr(__builtins__, "long"): # Python 3
    INT = int
    FLOAT = (float, int)
else: # Python 2
    INT = (int, long)
    FLOAT = (float, int, long)


###############################################################################
# Value Wrappers
###############################################################################

class RosValue(object):
    __slots__ = ()

    def __init__(self):
        raise NotImplementedError()

    @property
    def ros_type(self):
        raise NotImplementedError()

    @property
    def type_name(self):
        raise NotImplementedError()

    @property
    def is_dynamic(self):
        raise NotImplementedError()


class RosLiteral(RosValue):
    __slots__ = ("value",)

    @property
    def is_dynamic(self):
        return False

    def __eq__(self, other):
        if not isinstance(other, RosLiteral):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr(self.value))


class RosBool(RosLiteral):
    __slots__ = RosLiteral.__slots__

    def __init__(self, value):
        if isinstance(value, int):
            if value != 0 and value != 1:
                raise ValueError("invalid bool conversion: " + repr(value))
        if not isinstance(value, bool):
            raise TypeError("expected a bool value: " + repr(value))
        self.value = value

    @property
    def ros_type(self):
        return BOOL

    @property
    def type_name(self):
        return BOOL.type_name


class RosInt(RosLiteral):
    __slots__ = RosLiteral.__slots__ + ("_type",)

    def __init__(self, value, type_token):
        if not type_token in ROS_INT_TYPES:
            raise ValueError("expected an int type: " + repr(type_token))
        if (value is True or value is False
                or not isinstance(value, INT)):
            raise TypeError("expected an int value: " + repr(value))
        if value < type_token.min_value or value > type_token.max_value:
            raise ValueError("value out of range: " + repr(value))
        self.value = value
        self._type = type_token

    @property
    def ros_type(self):
        return self._type

    @property
    def type_name(self):
        return self._type.type_name

    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, repr(self.value),
                                   repr(self._type))


class RosFloat(RosLiteral):
    __slots__ = RosLiteral.__slots__ + ("_type",)

    def __init__(self, value, type_token):
        if not type_token in ROS_FLOAT_TYPES:
            raise ValueError("expected a float type: " + repr(type_token))
        if (value is True or value is False
                or not isinstance(value, FLOAT)):
            raise TypeError("expected a float value: " + repr(value))
        if value < type_token.min_value or value > type_token.max_value:
            raise ValueError("value out of range: " + repr(value))
        self.value = value
        self._type = type_token

    @property
    def ros_type(self):
        return self._type

    @property
    def type_name(self):
        return self._type.type_name

    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, repr(self.value),
                                   repr(self._type))


class RosString(RosLiteral):
    __slots__ = RosLiteral.__slots__

    def __init__(self, value):
        if not isinstance(value, basestring):
            raise TypeError("expected a string value: " + repr(value))
        self.value = value

    @property
    def ros_type(self):
        return STRING

    @property
    def type_name(self):
        return STRING.type_name
