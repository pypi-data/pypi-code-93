#!/usr/bin/env python3
# coding: utf-8

__version__ = '0.5.0'


def regular_cast(original, *try_funcs):
    """
    >>> regular_cast('12.3', int, float)
    12.3
    >>> regular_cast('12.3a', int, float)
    '12.3a'
    >>> regular_cast('12.3a', int, float, 0)
    0
    """
    for atmpt in try_funcs:
        if not callable(atmpt):
            return atmpt
        try:
            return atmpt(original)
        except (TypeError, ValueError):
            pass
    return original


def regular_lookup(dictlike, *try_keys):
    for key in try_keys:
        try:
            return dictlike[key]
        except LookupError:
            pass


def regular_attr_lookup(dictlike, *try_attrnames):
    for key in try_attrnames:
        try:
            return getattr(dictlike, key)
        except AttributeError:
            pass


def cache_lookup(dictlike, key, default, *args, **kwargs):
    try:
        return dictlike[key]
    except LookupError:
        pass
    if callable(default):
        value = default(*args, **kwargs)
    else:
        value = default
    dictlike[key] = value
    return value


def smart_cast(value, default):
    """
    Cast to the same type as `default`;
    if fail, return default
    :param value:
    :param default:
    :return:
    """
    func = type(default)
    try:
        return func(value)
    except (TypeError, ValueError):
        return default


def numerify(s):
    return regular_cast(s, int, float)


def want_bytes(s, **kwargs):
    """
    :param s: 
    :param kwargs: key word arguments passed to str.encode(..)
    :return: 
    """
    if not isinstance(s, bytes):
        s = s.encode(**kwargs)
    return s


def want_str(s, **kwargs):
    """
    :param s:
    :param kwargs: key word arguments passed to s.decode(..)
    :return:
    """
    if not isinstance(s, str):
        return s.decode(**kwargs)
    return s


want_unicode = want_str


def represent(obj, params):
    """
    :param obj:
    :param params: a dict or list
    """
    c = obj.__class__.__name__
    if isinstance(params, dict):
        parts = ('{}={}'.format(k, repr(v)) for k, v in params.items())
    else:
        parts = ('{}={}'.format(k, repr(getattr(obj, k))) for k in params)
    s = ', '.join(parts)
    return '<{}({}) at {}>'.format(c, s, hex(id(obj)))
