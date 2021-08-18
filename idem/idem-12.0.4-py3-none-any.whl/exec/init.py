from typing import Any
from typing import NamedTuple


class ExecReturn(NamedTuple):
    result: bool
    ret: Any
    comment: Any = None
    ref: str = ""

    def __bool__(self):
        return self.result

    def __getitem__(self, item):
        if item in self._fields:
            return getattr(self, item)
        return tuple.__getitem__(self, item)
