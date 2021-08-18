# -*- coding: utf-8 -*-
# Author: Ztj
# Email: ztj1993@gmail.com

import os

from ApolloClient import ApolloClient
from ConfigRegistry import ConfigRegistry


class ApolloConfig(object):
    def __init__(self, prefix):
        self._apollo = None
        self._setting = None
        self.prefix = (prefix if prefix.endswith('_') else prefix + '_').upper()

    @property
    def setting(self):
        if self._setting is None:
            self._setting = ConfigRegistry()
        return self._setting

    @setting.setter
    def setting(self, value):
        if isinstance(value, dict):
            value = ConfigRegistry(value)
        elif isinstance(value, ConfigRegistry):
            raise ValueError('setting is not ConfigRegistry')
        self._setting = value

    @property
    def apollo(self):
        if self._apollo is not None:
            return self._apollo
        client = ApolloClient.env()
        if client is None:
            raise AttributeError('apollo is not set')
        else:
            self._apollo = client
        return self._apollo

    @apollo.setter
    def apollo(self, value):
        if not isinstance(value, ApolloClient):
            raise ValueError('apollo is not ApolloClient')
        self._apollo = value

    def init(self):
        self.apollo.pull()
        for key, val in self.apollo.setting.items():
            self.setting.set(key, val)

        for key, value in os.environ.items():
            if not key.startswith(self.prefix): continue
            key = key[len(self.prefix):].lower().replace('_', '.')
            if not key: return False
            self.setting.set(key, value)

    def get(self, key, default=None, apollo=False, env=False):
        value = self.setting.get(key)
        if apollo is True:
            value = self.apollo.get(key, cache=False)
        if env is True:
            name = self.prefix + key.upper()
            value = os.environ.get(name)
        if value is None and default is not None:
            value = default
        return value
