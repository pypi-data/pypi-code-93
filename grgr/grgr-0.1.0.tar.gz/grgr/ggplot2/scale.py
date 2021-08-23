from copy import copy

import grgr.dev.typing as tp
from grgr.dev import _filter_none, dict_to_rargs, iter_to_rargs


class Appearance(tp.Join):
    """
    Appearance is a class that control the plot apperance.
    """
    def __init__(self, name: str, *args, **kwargs):
        self._s = str()
        reqargs = dict_to_rargs(locals(), ["name"])
        posargs = iter_to_rargs(args)
        kwargs = dict_to_rargs(kwargs, ["name"])
        rargs = ",".join(_filter_none([reqargs, posargs, kwargs]))
        if rargs is not None:
            self._s = f"{name}({rargs})"
        else:
            self._s = f"{name}()"

    def __repr__(self) -> str:
        return self._s

    def __add__(self, other: tp.Join) -> "Appearance":
        clone = copy(self)
        clone._s += f" + \n  {other.tor()}"
        return clone

    def tor(self) -> tp.RCode:
        return self._s
