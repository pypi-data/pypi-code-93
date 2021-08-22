import collections
import numpy as np

def isnumber(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

def isint(v):
    return isinstance(v, int) and not isinstance(v, bool)

def islistts(v, lo=0, hi=np.inf):
    return isinstance(v, collections.abc.Iterable) and all([isnumber(t) and lo <= t <= hi for t in v])

class ddict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delattr__

def defaults(opts, defs):
    return ddict({**defs, **opts})