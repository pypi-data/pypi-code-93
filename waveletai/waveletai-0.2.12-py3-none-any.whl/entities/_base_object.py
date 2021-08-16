#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2020/6/30 10:09
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : _base_object.py
@Desc    : base entity
"""
import pprint


class _BaseObject(object):
    def __iter__(self):
        # Iterate through list of properties and yield as key -> value
        for prop in self._properties():
            yield prop, self.__getattribute__(prop)

    @classmethod
    def _get_properties_helper(cls):
        return sorted([p for p in cls.__dict__ if isinstance(getattr(cls, p), property)])

    @classmethod
    def _properties(cls):
        return cls._get_properties_helper()

    def __repr__(self):
        return to_string(self)

    def to_string(self):
        return to_string(self)


def to_string(obj):
    return _ObjectPrinter().to_string(obj)


def get_classname(obj):
    return type(obj).__name__


class _ObjectPrinter(object):

    def __init__(self):
        super(_ObjectPrinter, self).__init__()
        self.printer = pprint.PrettyPrinter()

    def to_string(self, obj):
        # print(obj)
        # print(isinstance(obj, _BaseObject))
        if isinstance(obj, _BaseObject):
            return "<%s: %s>" % (get_classname(obj), self._entity_to_string(obj))
        return self.printer.pformat(obj)

    def _entity_to_string(self, entity):
        return ", ".join(["%s=%s" % (key, self.to_string(value)) for key, value in entity])
