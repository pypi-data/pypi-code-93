# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
# Copyright © 2021 André Santos

###############################################################################
# Imports
###############################################################################

# Python 2 and 3: forward-compatible
from __future__ import unicode_literals
from builtins import object, str


###############################################################################
# Type Tokens
###############################################################################

class TypeToken(object):
    __slots__ = ()

    @property
    def type_name(self):
        raise NotImplementedError()

    @property
    def is_builtin(self):
        return False

    @property
    def is_primitive(self):
        return False

    @property
    def is_number(self):
        return False

    @property
    def is_int(self):
        return False

    @property
    def is_float(self):
        return False

    @property
    def is_bool(self):
        return False

    @property
    def is_string(self):
        return False

    @property
    def is_time(self):
        return False

    @property
    def is_duration(self):
        return False

    @property
    def is_message(self):
        return False

    @property
    def is_header(self):
        return False

    @property
    def is_array(self):
        return False

    def __eq__(self, other):
        if not isinstance(other, TypeToken):
            return False
        return self.type_name == other.type_name

    def __hash__(self):
        return hash(self.type_name)

    def __str__(self):
        return self.type_name

    def __repr__(self):
        return "{}()".format(type(self).__name__)


class MessageType(TypeToken):
    __slots__ = ("_type", "fields", "constants")

    def __init__(self, type_name, fields, constants=None):
        # type_name :: string
        # fields :: dict(string, TypeToken)
        # constants :: dict(string, RosLiteral)
        self._type = type_name
        self.fields = fields
        self.constants = constants if constants is not None else {}

    @property
    def type_name(self):
        return self._type

    @property
    def is_message(self):
        return True

    @property
    def is_builtin(self):
        return self.is_header

    @property
    def is_header(self):
        return self._type == "std_msgs/Header"

    @property
    def package(self):
        return self._type.split("/")[0]

    @property
    def message(self):
        return self._type.split("/")[-1]

    def leaf_fields(self, name="msg", inc_arrays=False):
        primitives = {}
        arrays = {}
        stack = [(name, self)]
        while stack:
            name, type_token = stack.pop()
            if type_token.is_message:
                for field_name, field_type in type_token.fields.items():
                    n = "{}.{}".format(name, field_name)
                    stack.append((n, field_type))
            elif type_token.is_array:
                arrays[name] = type_token
            else:
                assert type_token.is_primitive
                primitives[name] = type_token
        if inc_arrays:
            primitives.update(arrays)
            return primitives
        else:
            return primitives, arrays

    def __repr__(self):
        return "{}({}, {}, constants={})".format(type(self).__name__,
            repr(self.type_name), repr(self.fields), repr(self.constants))


class ArrayType(TypeToken):
    __slots__ = ("type_token", "length")

    def __init__(self, type_token, length=None):
        # type_token :: TypeToken
        # length :: int >= 0
        self.type_token = type_token
        self.length = length

    @property
    def type_name(self):
        return self.type_token.type_name

    @property
    def is_builtin(self):
        return self.type_token.is_builtin

    @property
    def is_primitive(self):
        return self.type_token.is_primitive

    @property
    def is_number(self):
        return self.type_token.is_number

    @property
    def is_int(self):
        return self.type_token.is_int

    @property
    def is_float(self):
        return self.type_token.is_float

    @property
    def is_bool(self):
        return self.type_token.is_bool

    @property
    def is_string(self):
        return self.type_token.is_string

    @property
    def is_time(self):
        return self.type_token.is_time

    @property
    def is_duration(self):
        return self.type_token.is_duration

    @property
    def is_header(self):
        return self.type_token.is_header

    @property
    def is_message(self):
        return False

    @property
    def is_array(self):
        return True

    @property
    def is_fixed_length(self):
        return self.length is not None

    def contains_index(self, index):
        return (index >= 0 and (self.length is None or index < self.length))

    def __eq__(self, other):
        if not isinstance(other, ArrayType):
            return False
        return (self.type_token == other.type_token
                and self.length == other.length)

    def __hash__(self):
        return 31 * hash(self.type_token) + hash(self.length)

    def __str__(self):
        return "{}[{}]".format(self.type_token,
            "" if self.length is None else self.length)

    def __repr__(self):
        return "{}({}, length={})".format(type(self).__name__,
            repr(self.type_token), repr(self.length))
