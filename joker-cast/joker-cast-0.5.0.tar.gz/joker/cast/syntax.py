#!/usr/bin/env python3
# coding: utf-8

"""Syntax sugar"""


def noop(*_, **__):
    pass


def default_func(*pargs, **_):
    """
    As a placeholder function, it works like lambda x: x.
    As a method of a class, it returns cls or self.
    :param pargs: positional arguments
    :param _: keyword arguments, ignored
    :return: 1st positional arguments
    """
    return pargs[0]


def adaptive_call(entry):
    """
    >>> import sys
    >>> entry = [print, ['a', 'b'], {'file': sys.stderr}]
    >>> adaptive_call(entry)

    :param entry: an iterable or a callable
    :return:
    """
    pargs = []
    kwargs = dict()
    if callable(entry):
        return entry()

    items = list(entry)
    if not items:
        return items
    if not callable(items[0]):
        raise TypeError('first item of entry must be a callable')

    for x in items[1:]:
        if isinstance(x, (list, tuple)):
            pargs.extend(x)
        elif isinstance(x, dict):
            kwargs.update(x)
        else:
            raise TypeError('params must be a tuple, list or dict')
    return items[0](*pargs, **kwargs)


# TODO: be more general
def printerr(*args, **kwargs):
    import sys
    kwargs.setdefault('file', sys.stderr)
    pargs = []
    for a in args:
        if isinstance(a, BaseException):
            pargs.append(a.__class__.__name__)
            pargs.append(str(a))
            kwargs.setdefault('sep', ': ')
        else:
            pargs.append(a)
    print(*pargs, **kwargs)


def instanciate(cls):
    return cls()


def instanciate_with_foolproof(cls):
    """
    The return class can be called again without error
    """
    if '__call__' not in cls.__dict__:
        cls.__call__ = lambda x: x
    return cls()


class ConstantCallable(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)


_always_true = ConstantCallable(True)
_always_false = ConstantCallable(False)


class Void(object):
    """
    Act as 0, False, '', [] 
    """
    __bool__ = _always_false
    __nonzero__ = _always_false
    __add__ = default_func
    __sub__ = default_func
    __radd__ = default_func
    __rsub__ = default_func
    __round__ = default_func
    __truediv__ = default_func
    __floordiv__ = default_func
    __rtruediv__ = default_func
    __rfloordiv__ = default_func
    __rmul__ = default_func
    __gt__ = _always_false
    __ge__ = _always_false
    __lt__ = _always_false
    __le__ = _always_false
    __len__ = ConstantCallable(0)

    def __init__(self, symbol='-'):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.symbol))

    def __eq__(self, other):
        if isinstance(other, Void):
            return True
        return False


Object = type('Object', (object,), {})


class Universe(object):
    __contains__ = _always_true
    __iter__ = ConstantCallable(tuple())


class Mu(object):
    __slots__ = ['value']

    # mutable value
    def __init__(self, value):
        self.value = value

    def __call__(self, value):
        self.value = value
        return self


class Glass(object):
    def __getattr__(self, name):
        return globals().get(name)
