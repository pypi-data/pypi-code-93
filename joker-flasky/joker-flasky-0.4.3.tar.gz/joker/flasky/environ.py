#!/usr/bin/env python3
# coding: utf-8

import json

import volkanic
from volkanic.compat import cached_property


class GlobalInterface(volkanic.GlobalInterface):
    package_name = 'joker.flasky'

    @cached_property
    def mime_types(self) -> dict:
        path = self.under_package_dir('kb/mime-types.json')
        return json.load(open(path))
