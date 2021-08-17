from typing import Union
from collections import defaultdict

from .dispatch import MultiDispatch
from .isa import PythonTyping
from .utils import bfs
from . import Dispatch

class CastError(Exception):
    pass


_cast_dispatch = MultiDispatch(PythonTyping(), test_subtypes=[1])


class CastGraph:
    def __init__(self):
        self.casts = defaultdict(dict)

    def add_cast(self, srcs, dsts, auto=False):
        if not isinstance(srcs, tuple):
            srcs = (srcs,)
        if not isinstance(dsts, tuple):
            dsts = (dsts,)

        for src in srcs:
            for dst in dsts:
                src_casts = self.casts[src]
                assert dst not in src_casts, "cast already defined!"
                src_casts[dst] = auto

    def find_route(self, src, dst):
        if dst in self.casts[src]:
            return [dst]

        breadcrumbs = {}
        def expand(n):
            for k in self.casts[n]:
                if k not in breadcrumbs:
                    breadcrumbs[k] = n
                yield k
        for x in bfs([src], expand):
            if x == dst:
                break
        else:
            raise CastError(f"Couldn't find a cast path: {src} to {dst}")

        x = dst
        path = []
        while x != src:
            path.append(x)
            x = breadcrumbs[x]
        path.reverse()

        return path

_cast_graph = CastGraph()

def def_cast(f=None, auto=False):
    def wrapper(f):
        # TODO
        assert f.__name__ == 'cast_to'
        src, dst = f.__annotations__.values()
        _cast_graph.add_cast(src, dst, auto=auto)
        return _cast_dispatch(f)

    if f is not None:
        return wrapper(f)

    return wrapper

def cast(obj, to_type, routed=True):
    """Casts from obj to the given type, if such a cast is defined

    If routed is True, and the direct cast doesn't exist, the cast will be attempted by a performing chain of casts, if such exists.
    """
    res = obj
    for t in _cast_graph.find_route(type(obj), to_type):
        res = cast_to(res, t)

    return res

def list_casts(src_type=None, dst_type=None):
    assert dst_type is None, "Not implemented yet"

    return _cast_graph.casts[src_type]


@def_cast   
def cast_to(i: (int, float, str, list, tuple, dict), cls: bool):
    return cls(i)

@def_cast
def cast_to(i: (int, float, bool), cls: str):
    return cls(i)

@def_cast(auto=True)
def cast_to(d: dict, cls: (iter, list)):
    return cls(d.items())

@def_cast(auto=True)
def cast_to(i: (tuple, set, frozenset, iter), cls: list):
    return cls(i)

# @def_cast(auto=True)
# def cast_to(l: (list, str), cls: iter):
#     return cls(l)


# Pair = Type(tuple, length=2)


@def_cast
def cast_to(l: (iter, list), cls:dict):
    try:
        return cls(l)
    except ValueError:
        raise CastError()

@def_cast
def cast_to(l: list, cls:tuple):
    return cls(l)


from pathlib import Path

@def_cast(auto=True)
def cast_to(s: str, cls: Path):
    return cls(s)


class ExistingPath(type(Path())):
    pass

class Directory(ExistingPath):
    pass

@def_cast(auto=True)
def cast_to(p: Path, cls: ExistingPath):
    if not p.exists():
        raise CastError()
    return cls(p)

@def_cast(auto=True)
def cast_to(p: Path, cls: Directory):
    if not p.is_dir():
        raise CastError("Not a directory")
    return cls(p)




class SortedList(list):
    pass

@def_cast(auto=True)
def cast_to(l: list, cls: SortedList):
    return cls(sorted(l))




# print(cast_to((1,2), list))

print(cast_to('a', Path))
print(cast_to(Path('/code/casts.py'), ExistingPath))
print(cast_to(Path('/code'), Directory))

# print(cast_to(Path('/code/casts.py'), Directory))




# print(cast('/code', ExistingPath))

res = (cast([6,5,3], SortedList))
# print(res)

print(cast(res, SortedList))
print(cast(res + [1], SortedList))
print(cast((4,2), list))
print(cast((4,2), SortedList))
print(cast({4,2}, SortedList))

#print(cast(iter({4,2}), SortedList)) # TODO

dp = Dispatch()

@dp
def my_min(l: list):
    print("regular", l)
    return min(l)

@dp
def my_min(l: SortedList):
    print("sorted", l)
    return l[0]



print( my_min( [6,4,5] ))
print( my_min( cast([6,4,5], SortedList) ))



from typing import List
@def_cast(auto=True)
def cast_to(obj: list, cls: List[str]):
    return list(cast(x, str) for x in obj)

@def_cast(auto=True)
def cast_to(obj: list, cls: List[int]):
    return list(cast(x, int) for x in obj)


print(cast([1,2], List[str]))
print(cast(cast([1,2], List[str]), tuple))
