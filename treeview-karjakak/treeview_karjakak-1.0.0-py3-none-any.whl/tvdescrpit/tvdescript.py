# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

import re
import weakref
from types import GeneratorType
from functools import wraps

class DescriptClasses(type):
    
    def __new__(cls, name, bases, cls_d):
        CLS_NAMES = ['ChildsNum', 'Parent', 'FileName']
        
        clsob = super().__new__(cls, name, bases, cls_d)
        
        if name == CLS_NAMES[2]:
            setattr(clsob, 'store1', dict())        
        
        def _set(clsob, instance, value):
            return NotImplemented
        
        if name in CLS_NAMES[:2]:
            setattr(clsob, '__set__', _set)
        
        def getchild(clsob, instance, owner_class):
            if clsob.totr is None:
                clsob.totr = (clsob.childs * clsob.spc) + 1
            spc = clsob.spc
            return ((f'child{c//spc}', c) for c in range(clsob.totr) if c % spc == 0 and c != 0)
        
        if name == CLS_NAMES[0]:
            setattr(clsob, '__get__', getchild)
        
        def getpar(clsob, instance, owner_class):
            return enumerate(('parent',))
        
        if name == CLS_NAMES[1]:
            setattr(clsob, '__get__', getpar)
        
        def getfil(clsob, instance, owner):
            if instance is None:
                return clsob
            else:
                return clsob.store1[id(instance)][1]
        
        if name == CLS_NAMES[2]:
            setattr(clsob, '__get__', getfil)
    
        def setfil(clsob, instance, value):
            if id(instance) not in clsob.store1:
                clsob.store1[id(instance)] = \
                    (weakref.ref(instance, clsob.finalize), value)
        
        if name == CLS_NAMES[2]:
            setattr(clsob, '__set__', setfil)
        
        def finalize(clsob, weak_ref):
            look = [key for key, value in clsob.store1.items()
                    if value[0] is weak_ref]
            if look:
                del clsob.store1[look[0]]
        
        if name == CLS_NAMES[2]:
            setattr(clsob, 'finalize', finalize)

        def delch(clsob, instance):
            del instance, clsob
        
        if name in CLS_NAMES:
            setattr(clsob, '__delete__', delch)
                
        return clsob

class ChildsNum(metaclass=DescriptClasses):
    
    def __init__(self, childs, spc):
        if isinstance(childs, int) and isinstance(spc, int):
            self.childs = childs
            self.spc = spc
            self.totr = None
    
class Parent(metaclass=DescriptClasses):
    pass 
    
class FileName(metaclass=DescriptClasses):
    pass

class Gtv:
    """
    Generator for TreeView functions.
    """
    
    def editt(words, data, row) -> GeneratorType:
        """Generator for edit"""
        
        for n, d in data:
            if n != row:
                yield d
            else:
                if d != '\n':
                    yield words
                else:
                    yield words
                    yield d
    
    def insertr(words, data, row) -> GeneratorType:
        """ Generator for insert"""
        keep = [] 
        for n, d in data:
            if n != 0 and n == row-1 and d == '\n':
                keep.append(d)
            elif n == row:
                yield words
                if keep:
                    yield keep[0]
                yield d
            else:
                yield d
        del keep
        
    def movet(data, row, to, great = False) -> GeneratorType:
        """Generator for move"""
        
        m = []
        if great:
            for n, d in data:
                if n == row:
                    m.append(d)
                else:
                    yield d
            yield m[0]
        else:
            if row < to:
                for n, d in data:
                    if n == row:
                        m.append(d)
                    elif n == to:
                        yield d
                        yield m[0]
                    else:
                        yield d
            else:
                for n, d in data:
                    if n < to:
                        yield d
                    elif n < row:
                        m.append(d)
                    elif n == row:
                        yield d
                        yield from m
                    else:
                        yield d
        del m

    def movec(data, row, child) -> GeneratorType:
        """Generator for moving child"""
        
        match = None
        for n, d in data:
            if n == row:
                if d != '\n':
                    match = re.match(r"\s+", d).span()[1]
                    yield f'{" " * child}{d[(match:=0 if not match else match):]}'
                else:
                    yield d
            else:
                yield d
    
    def genchek(data, row, stc) -> GeneratorType:
        """Generator for checked"""
        
        for n, d in data:
            if n == row:
                if d != '\n' and d[-2] != ':':
                    if stc not in d:
                        yield d[:-1] + stc + '\n'
                    else:
                        yield d.rpartition(stc)[0] + '\n'
                else:
                    yield d
            else:
                yield d
    
    def gensp(data, row):
        """Generator for insert space"""
        
        for n, d in data:
            if row != 0 and n == row:
                yield '\n'
            yield d

def configtv(childs = None, space = None):
    """Decorator for childs in TreeView."""
    
    def childnum(cls):
        @wraps(cls)
        def inner(arg):
            if childs and space:
                cls.childs = ChildsNum(childs, space)
            return cls(arg)
        return inner
    return childnum