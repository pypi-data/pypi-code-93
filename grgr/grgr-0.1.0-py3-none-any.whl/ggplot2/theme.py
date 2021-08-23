from copy import copy
from typing import Any, Dict

import grgr.dev.typing as tp
from grgr.dev import dict_to_rargs


class Theme(tp.Join):
    def __init__(self, name: str, **kwargs):
        self._s = str()
        pyargs_ = locals()
        pyargs_.update(kwargs)
        pyargs: Dict[str, Any] = dict()
        for k, v in pyargs_.items():
            # `.` can not be used in a variable name so relace `_` with `.`.
            s = k.replace("_", ".")
            pyargs[s] = v
        rargs = dict_to_rargs(pyargs, ["name", "pyargs_"])
        if rargs is not None:
            self._s = f"{name}({rargs})"
        else:
            self._s = f"{name}()"

    def __repr__(self) -> str:
        return self._s

    def __add__(self, other: tp.Join) -> "Theme":
        clone = copy(self)
        clone._s += f" + \n  {other.tor()}"
        return clone

    def tor(self) -> tp.RCode:
        return self._s


class ThemeElement(tp.Tor):
    def __init__(self, name: str, **kwargs):
        self._s = str()
        pyargs = locals()
        pyargs.update(kwargs)
        rargs = dict_to_rargs(pyargs, ["name"])
        if rargs is not None:
            self._s = f"{name}({rargs})"
        else:
            self._s = f"{name}()"

    def __repr__(self) -> str:
        return self._s

    def tor(self) -> tp.RCode:
        return self._s
