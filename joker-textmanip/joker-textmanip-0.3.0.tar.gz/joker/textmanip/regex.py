#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import re

from joker.textmanip.align import commonprefix, commonsuffix


def infer_affix_pattern(strings):
    strings = list(set(x or '' for x in strings))
    if not strings:
        return '.*'

    if len(strings) == 1:
        return re.escape(list(strings)[0])

    prefix = commonprefix(strings)
    suffix = commonsuffix(strings)
    a = len(prefix)
    b = - len(suffix) or None
    strings = [x[a:b] for x in strings]

    minlen = min(len(x) for x in strings)
    maxlen = max(len(x) for x in strings)

    strings = [re.escape(x) for x in strings if x]
    strings.sort()

    if maxlen == 1:
        if len(strings) == 1:
            ptn = strings[0]
        else:
            ptn = '[{}]'.format(''.join(strings))
    else:
        ptn = '|'.join(strings)
        ptn = '(?:{})'.format(ptn)

    if minlen == 0:
        ptn += '?'
    return re.escape(prefix) + ptn + re.escape(suffix)


def _optchr(i):
    if 48 <= i <= 90:
        return chr(i)
    return r'\u{:04X}'.format(i)


def make_range_pattern(blocks):
    """
    >>> blks = [(48, 50), 65]
    >>> make_range_pattern(blks)
    '0-2A'
    """
    parts = []
    for tuple_or_int in blocks:
        if isinstance(tuple_or_int, tuple):
            p = '{}-{}'.format(*map(_optchr, tuple_or_int[:2]))
            parts.append(p)
        else:
            parts.append(chr(tuple_or_int))
    return ''.join(parts)
