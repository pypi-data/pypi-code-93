#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, unicode_literals

import collections
import re

_cache = {}

cjk_blocks = [
    (0x2E80, 0x2EFF, "CJK Radicals Supplement"),
    (0x3000, 0x303F, "CJK Symbols & Punctuation"),
    (0x31C0, 0x31EF, "CJK Strokes"),
    (0x3200, 0x32FF, "CJK Enclosed Letters and Months"),
    (0x3300, 0x33FF, "CJK Compatibility"),
    (0x3400, 0x4DBF, "CJK Unified Ideographs Extension A"),
    (0x4E00, 0x9FFF, "CJK Unified Ideographs"),
    (0xF900, 0xFAFF, "CJK Compatibility Ideographs"),
    (0xFE30, 0xFE4F, "CJK Compatibility Forms"),
]


def _cjk():
    try:
        return _cache['_cjk']
    except KeyError:
        from joker.textmanip.regex import make_range_pattern
        return make_range_pattern(cjk_blocks)


def remove_cjk(text):
    print('_cjk', repr(_cjk()))
    return re.sub('[{}]'.format(_cjk()), '', text)


def remove_spaces_beside_cjk(text):
    parts = re.split(r'\s*([{}]+)\s*'.format(_cjk()), text)
    return ''.join(parts)


def remove_spaces_between_cjk(text):
    return re.sub(r'([{0}]+)\s+(?=[{0}])'.format(_cjk()), r'\1', text)


def _filter_encodings(s, func):
    from joker.textmanip.data import get_all_encodings
    viable_encodings = list()
    for enc in get_all_encodings():
        try:
            func(s, enc)
            viable_encodings.append(enc)
        except ValueError:
            pass
    return viable_encodings


def who_can_encode(text):
    return _filter_encodings(text, lambda x, c: x.encode(c))


def who_can_decode(text):
    return _filter_encodings(text, lambda x, c: x.encode(c))


def _encode(text, enc):
    try:
        return text.encode(enc)
    except Exception:
        pass


def _decode(text, dec):
    try:
        return text.decode(dec)
    except Exception:
        pass


def brutal_cjk_decode(text, lang='sc'):
    from joker.textmanip.data import (
        get_most_frequent_characters, get_all_encodings)

    available_encodings = get_all_encodings()
    candidates = collections.defaultdict(list)
    if not isinstance(text, bytes):
        for enc in available_encodings:
            candidates[_encode(text, enc)].append(enc)
        candidates.pop(None, [])
    else:
        candidates[text] = [None]

    results = collections.defaultdict(list)
    for binary, encs in candidates.items():
        for dec in available_encodings:
            results[_decode(binary, dec)].append((dec, encs))
    results.pop(None, [])

    if not results:
        return None, 0, []

    scores = []
    mfc = set(get_most_frequent_characters(lang))
    for rs in results:
        # print(rs, repr(rs))
        sc = len([1 for x in rs if x in mfc]) / len(rs)
        scores.append((sc, rs))
    scores.sort(reverse=True)

    sc, rs = scores[0]
    return rs, sc, results[rs]


chsi_digits = '零一二三四五六七八九'

chtr_digits = '零壹贰叁肆伍陆柒捌玖'

punctuations = [
    ('(', '\uff08'),
    (')', '\uff09'),
    ('.', '\u3002'),
    (',', '\uff0c'),
]


def _repdiv(num, divisor):
    results = []
    while num:
        d, m = divmod(num, divisor)
        results.append(m)
        num = d
    return results


def i2ch_lt10k(num, digits, units):
    parts = collections.deque()
    for u, n in enumerate(_repdiv(num, 10)):
        if n:
            parts.appendleft(units[u])
        parts.appendleft(digits[n])
    ch = ''.join(parts)
    ch = re.sub(r'零+$', '', ch, flags=re.UNICODE)
    ch = re.sub(r'零{2,}', '零', ch, flags=re.UNICODE)
    ch = re.sub(r'\s+', '', ch, flags=re.UNICODE)
    return ch


def i2chsi(num, digits, units):
    num = int(num)
    if num < 10:
        return digits[num]
    if num == 10:
        return units[1]
    if num < 20:
        return units[1] + digits[num % 10]
    parts = collections.deque()
    for u8, n8 in enumerate(_repdiv(num, 10 ** 8)):
        if u8:
            parts.appendleft(units[5])
        for u4, n4 in enumerate(_repdiv(n8, 10 ** 4)):
            if u4:
                parts.appendleft(units[4])
            ch = i2ch_lt10k(n4, digits, units)
            parts.appendleft(ch)
    return ''.join(parts)


def integer_to_chsi(num):
    """Simplified characters used in mainland China"""
    return i2chsi(num, chsi_digits, ['', '十', '百', '千', '万', '亿'])


def integer_to_chsicap(num):
    """Tamper-safe characters used in mainland China"""
    return i2chsi(num, chtr_digits, ['', '拾', '佰', '仟', '万', '亿'])


def chinese_to_integer():
    raise NotImplementedError


_map_chsi_0110 = {
    '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
    '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
}

_map_chsi_1120 = {
    '十一': '11', '十二': '12', '十三': '13', '十四': '14', '十五': '15',
    '十六': '16', '十七': '17', '十八': '18', '十九': '19', '二十': '20',
}


def replace_small_chsi_with_decimal(s):
    regex = re.compile(r'[一二三四五六七八九十]+', re.UNICODE)
    for _map in [_map_chsi_1120, _map_chsi_0110]:
        s = regex.sub(lambda m: _map[m.group()], s)
    return s


def replace_small_decimal_with_chsi(s):
    regex = re.compile(r'\d+')
    return regex.sub(lambda m: integer_to_chsi(m.group()), s)


def as_translation_table(func):
    """ret.__getitem__ = func"""
    attrs = {'__getitem__': staticmethod(func)}
    return type('translation_table', tuple(), attrs)()


@as_translation_table
def to_halfwidth(ordinal):
    ordinal -= 0xFEE0
    if 32 < ordinal < 127:
        return chr(ordinal)
    raise LookupError


@as_translation_table
def to_fullwidth(ordinal):
    if 32 < ordinal < 127:
        return chr(ordinal + 0xFEE0)
    raise LookupError
