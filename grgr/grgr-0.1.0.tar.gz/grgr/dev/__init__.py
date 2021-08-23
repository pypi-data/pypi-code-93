""" A module where helper functions for development are implemented """
from typing import Any, Dict, Iterable, List, Optional

import grgr.dev.typing as tp
from grgr import _R
from numpy import ndarray
from pandas import DataFrame
from rpy2.robjects import conversion, default_converter, numpy2ri, pandas2ri


def _is_ndarray(x: Any) -> bool:
    return isinstance(x, ndarray)


def _is_dataframe(x: Any) -> bool:
    return isinstance(x, DataFrame)


def _is_ggplot(x: Any) -> bool:
    return isinstance(x, tp.Show)


def assign_in_R(varname: str, v: Any):
    if _is_ggplot(v):
        _R(f"{varname} <- {v.tor()}")
        return None
    if _is_ndarray(v):
        with conversion.localconverter(default_converter + numpy2ri.converter):
            v = conversion.py2rpy(v)
    if _is_dataframe(v):
        with conversion.localconverter(default_converter +
                                       pandas2ri.converter):
            v = conversion.py2rpy(v)
    _R.assign(varname, v)


def _id_to_alphabet(x: Any) -> str:
    id_ = str(id(x))
    return "".join((map(lambda i: chr(ord("@") + int(i) + 1), str(id_))))


def _format_as_kwarg(k: str, v: Any, ignored: List[str]) -> Optional[str]:
    if v is None or k in ignored:
        return None
    if _is_ndarray(v) or _is_dataframe(v) or _is_ggplot(v):
        varname = _id_to_alphabet(v)
        assign_in_R(varname, v)
        return f"{k}={varname}"
    return f"{k}={v}"


def _format_as_posarg(v: Any) -> str:
    if _is_ndarray(v) or _is_dataframe(v) or _is_ggplot(v):
        varname = _id_to_alphabet(v)
        assign_in_R(varname, v)
        return (varname)
    return str(v)


def _filter_none(x: Iterable[Optional[Any]]) -> filter:
    return filter(lambda x_: x_ is not None, x)


def dict_to_rargs(d: Dict, ignored: List[str] = []) -> Optional[tp.RCode]:
    # following three variables are ignored by defalut
    ignored.extend(["ignores", "self", "args", "kwargs"])
    _fargs: map[Optional[str]] = map(
        lambda kv: _format_as_kwarg(kv[0], kv[1], ignored), d.items())
    fargs = list(_filter_none(_fargs))
    s = ",".join(fargs)
    if len(s) == 0:
        return None
    return s


def iter_to_rargs(x: Iterable) -> Optional[tp.RCode]:
    fargs: map[str] = map(_format_as_posarg, x)
    s = ",".join(fargs)
    if len(s) == 0:
        return None
    return s
