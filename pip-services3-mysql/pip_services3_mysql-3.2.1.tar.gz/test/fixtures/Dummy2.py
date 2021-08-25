# -*- coding: utf-8 -*-

from pip_services3_commons.data import IIdentifiable


class Dummy2(IIdentifiable):
    def __init__(self, id: int = None, key: str = None, content: str = None):
        self.id = id
        self.key = key
        self.content = content
