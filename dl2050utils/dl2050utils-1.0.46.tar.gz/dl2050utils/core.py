from typing import *
import operator
import re
from collections.abc import Iterable,Iterator,Generator,Collection

def oget(o, fs, default_=None):
    for f in fs:
        if f is None or f not in o: return default_
        o = o[f]
    return o

def test(a,b,cmp,cname=None):
    if cname is None: cname=cmp.__name__
    assert cmp(a,b),f"{cname}:\n{a}\n{b}"
def test_eq(a,b): test(a,b,operator.eq,'==')

def ifnone(a, b): return b if a is None else a
def setify(o): return o if isinstance(o,set) else set(listify(o))

def is_iter(o): return isinstance(o, (Iterable,Generator)) and getattr(o,'ndim',1)
def _is_array(x): return hasattr(x,'__array__') or hasattr(x,'iloc')
def listify(o):
    if o is None: return []
    if isinstance(o, list): return o
    if isinstance(o, str) or _is_array(o): return [o]
    if is_iter(o): return list(o)
    return [o]

def uniqueify(x, sort=False):
    res = list(OrderedDict.fromkeys(x).keys())
    if sort: res.sort()
    return res

class L():
    def __init__(self, items): self.items = listify(items)
    def __getitem__(self, idx):
        try: return self.items[idx]
        except TypeError:
            if isinstance(idx[0],bool):
                assert len(idx)==len(self) # bool mask
                return [o for m,o in zip(idx,self.items) if m]
            return [self.items[i] for i in idx]
    def __len__(self): return len(self.items)
    def __iter__(self): return iter(self.items)
    def __setitem__(self, i, o): self.items[i] = o
    def __delitem__(self, i): del(self.items[i])
    def __repr__(self):
        res = f'{self.__class__.__name__} ({len(self)} items)\n{self.items[:10]}'
        if len(self)>10: res = res[:-1]+ '...]'
        return res
    def append(self,o): return self.items.append(o)
    def remove(self,o): return self.items.remove(o)
    def unique(self): return L(dict.fromkeys(self).keys())
    def sort(self, key=None, reverse=False): return self.items.sort(key=key, reverse=reverse)
    def reverse(self ): return self.items.reverse()

_camel_re1 = re.compile('(.)([A-Z][a-z]+)')
_camel_re2 = re.compile('([a-z0-9])([A-Z])')
def camel2snake(name):
    s1 = re.sub(_camel_re1, r'\1_\2', name)
    return re.sub(_camel_re2, r'\1_\2', s1).lower()

def compose(x, funcs, *args, order_key='_order', **kwargs):
    key = lambda o: getattr(o, order_key, 0)
    for f in sorted(listify(funcs), key=key): x = f(x, **kwargs)
    return x
