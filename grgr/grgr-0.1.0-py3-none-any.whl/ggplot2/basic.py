""" A module where the core classes and functions of `ggplot2`  """
from copy import copy
from typing import Optional, Union

import grgr.dev.typing as tp
from grgr import _R
from grgr.dev import dict_to_rargs
from numpy import ndarray
from pandas import DataFrame


class Aesthetic(tp.Tor):
    def __init__(self,
                 x: Optional[Union[str, ndarray]] = None,
                 y: Optional[Union[str, ndarray]] = None,
                 **kwargs):
        self._s = str()
        pyargs = locals()
        pyargs.update(kwargs)
        rargs = dict_to_rargs(pyargs)
        if rargs is not None:
            self._s = f"aes({rargs})"
        else:
            self._s = "aes()"

    def __repr__(self) -> str:
        return self._s

    def tor(self) -> tp.RCode:
        return self._s


class GGPlot(tp.Join, tp.Show):
    def __init__(self,
                 data: Optional[DataFrame] = None,
                 mapping: Optional[Aesthetic] = None,
                 **kwargs):
        self._s = str()
        pyargs = locals()
        pyargs.update(kwargs)
        rargs = dict_to_rargs(pyargs)
        if rargs is not None:
            self._s = f"ggplot({rargs})"
        else:
            self._s = "ggplot()"

    def __repr__(self) -> str:
        self.show()
        return self._s

    def __add__(self, other: tp.Join) -> "GGPlot":
        clone = copy(self)
        clone._s += f" + \n  {other.tor()}"
        return clone

    def tor(self) -> tp.RCode:
        return self._s

    def show(self):
        print(_R(self._s))
