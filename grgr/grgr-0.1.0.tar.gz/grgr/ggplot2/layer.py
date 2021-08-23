""" Provide the vairous layers of `ggplot2` """
from copy import copy
from typing import Optional

import grgr.dev.typing as tp
from grgr.dev import dict_to_rargs
from grgr.ggplot2.basic import Aesthetic
from pandas import DataFrame


class Layer(tp.Join):
    def __init__(self,
                 name: str,
                 data: Optional[DataFrame] = None,
                 mapping: Optional[Aesthetic] = None,
                 **kwargs):
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

    def __add__(self, other: tp.Join) -> "Layer":
        clone = copy(self)
        clone._s += f" + \n  {other.tor()}"
        return clone

    def tor(self) -> tp.RCode:
        return self._s
