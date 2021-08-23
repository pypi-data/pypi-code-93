from collections.abc import MutableMapping
from functools import reduce
from typing import Any, Dict


def rec_merge(d1, d2) -> Dict[Any, Any]:
    """
    Update two dicts of dicts recursively,
    if either mapping has leaves that are non-dicts,
    the second's leaf overwrites the first's.
    """
    for k, v in d1.items():
        if k in d2:
            # this next check is the only difference!
            if all(isinstance(e, MutableMapping) for e in (v, d2[k])):
                d2[k] = rec_merge(v, d2[k])
            # we could further check types and merge as appropriate here.
    d3 = d1.copy()
    d3.update(d2)
    return d3


def merge(d1, d2) -> Dict[Any, Any]:
    return reduce(rec_merge, (d1, d2))
