from typing import Callable, Union

from pysome import Some, AllOf
from pysome.SameState import default_name, SameState
from pysome.exceptions import InvalidArgument, SameOutsideExpect


class Same(Some):
    state_name = "Same"

    def __init__(self, *args: Union[type, Callable, Some], name=default_name):
        self.some = Some(*args)
        if not hasattr(name, "__hash__"):
            raise InvalidArgument("name of 'Same' object must be hashable")
        self.name = name

        def validate_same(other):
            return self.state_check(other)

        super().__init__(AllOf(Some(*args), validate_same))  # todo: test

    def state_check(self, other):
        if SameState._allow[self.state_name] is False:  # noqa
            raise SameOutsideExpect("Same was used outside of an expect")

        if self.some != other:
            return False

        if self.name not in SameState._state[self.state_name]:
            SameState._state[self.state_name][self.name] = other  # noqa
            return True

        return self._eq(other)

    def _eq(self, other):
        return other == SameState._state[self.state_name][self.name]  # noqa


class NotSame(Same):
    state_name = "NotSame"

    def _eq(self, other):
        return not other == SameState._state[self.state_name][self.name]  # noqa


# alias
is_same = Same
is_unique = NotSame
