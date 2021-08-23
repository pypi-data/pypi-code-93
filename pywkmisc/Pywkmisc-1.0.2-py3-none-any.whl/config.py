#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import jsonpath


class Config(object):

    def __init__(self, cfp=None):
        self._cfp = cfp     # config_folder_path
        self._config: dict = {}
        self._check_path()
        self._get_config()

    def _check_path(self):
        if self._cfp is None:
            self._cfp = os.path.abspath('conf/')
        else:
            self._cfp = os.path.abspath(self._cfp)
        self._cfp = self._cfp.replace('\\', os.sep)
        self._cfp = self._cfp.replace('/', os.sep)
        if not self._cfp[len(self._cfp)-1] == os.sep:
            self._cfp += os.sep
        if not os.path.exists(self._cfp):
            raise RuntimeError('{}路径不存在'.format(self._cfp))

    def _get_config(self):
        for file in os.listdir(self._cfp):
            with open('{path}{file}'.format(path=self._cfp, file=file), 'r', encoding='utf8') as f:
                self._config[file.split('.', 2)[0]] = json.load(f)

    def get_basic(self, key):
        return self.get('base',key)

    def gets_basic(self, key):
        return self._gets('base', key)

    def get(self, c_type, key):
        return self._get(c_type, '$.{key}'.format(key=key))

    def gets(self, c_type, key):
        return self._gets(c_type, '$.{key}'.format(key=key))

    def _gets(self, c_type, key):
        return jsonpath.jsonpath(self._config[c_type], key)

    def _get(self, c_type, key):
        _v = self._gets(c_type, key)
        if _v:
            return _v[0]
