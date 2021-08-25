from __future__ import absolute_import
from __future__ import unicode_literals

from laipvt.sysutil.util import to_object

class ListHandler(object):
    def __init__(self, l: list):
        self.l = l
        self.iter = iter(l)

    def check(self, value: str) -> bool:
        return value in self.l

    def get(self) -> list:
        return self.l

    def next(self):
        try:
            return next(self.iter)
        except StopIteration:
            return False

    def length(self) -> int:
        return len(self.l)

class DictHandler(object):
    def __init__(self, d: dict):
        self.d = to_object(d)

    def get(self) -> dict:
        return self.d

    def length(self) -> int:
        return len(self.d)