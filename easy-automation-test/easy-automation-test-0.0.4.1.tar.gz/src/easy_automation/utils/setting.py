#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/20
import importlib


class Setting:

    def __init__(self):
        self.SETTING_MODULE = 'settings.settings'
        _settings = importlib.import_module(self.SETTING_MODULE)
        for setting in dir(_settings):
            if setting.isupper():
                value = getattr(_settings, setting)
                setattr(self, setting, value)

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            'cls': self.__class__.__name__,
            'settings_module': self.SETTING_MODULE,
        }


setting = Setting()
