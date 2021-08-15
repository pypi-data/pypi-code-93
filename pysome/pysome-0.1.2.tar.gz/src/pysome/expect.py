from typing import Any
from pysome import SameState


class expect:
    def __init__(self, data: Any):
        self.data = data

    def to_be(self, other):
        SameState._start()  # noqa
        assert other == self.data
        SameState._end()  # noqa
        return self

    def not_to_be(self, other):
        SameState._start()  # noqa
        assert not other == self.data
        SameState._end()  # noqa
        return self
