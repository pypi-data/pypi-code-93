#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import collections
import pprint

from joker.cast import numerify

from joker.textmanip import align
from joker.stream.shell import ShellStream


def _split2(s):
    parts = s.strip().split(None, 1)
    while len(parts) < 2:
        parts.append(None)
    return tuple(parts)


def text_numsum(lines):
    total = 0
    count = 0
    for x in lines:
        count += 1
        try:
            total += numerify(x)
        except (TypeError, ValueError):
            continue
    mean = 1. * total / count
    if total == int(total):
        total = int(total)
    if mean == int(mean):
        mean = int(mean)
    return total, mean


def text_to_list(lines):
    """Get a list of lists from lines of text"""
    if isinstance(lines, str):
        lines = lines.splitlines()
    return [lx.strip().split() for lx in lines]


def text_to_dict(lines, swap=False, ordered=False):
    """Get a dict or OrderedDict from lines of text"""
    if isinstance(lines, str):
        lines = lines.splitlines()
    tups = [_split2(x) for x in lines]
    if swap:
        tups = [tu[::-1] for tu in tups]
    if ordered:
        return collections.OrderedDict(tups)
    else:
        return dict(tups)


def textfile_numsum(path, printout=False):
    with ShellStream.open(path) as sstm:
        rv = text_numsum(sstm.dense())
        if printout:
            print(*rv)
        return rv


def textfile_to_list(path, printout=False):
    """Get a list of lists from a path to a text file"""
    with ShellStream.open(path) as sstm:
        rv = text_to_list(sstm.dense())
        if printout:
            pprint.pprint(rv)
        return rv


def textfile_to_dict(path, swap=False, ordered=False, printout=False):
    """Get a dict from a path to a text file"""
    with ShellStream.open(path) as sstm:
        rv = text_to_dict(sstm.dense(), swap=swap, ordered=ordered)
        if printout:
            pprint.pprint(rv, indent=4)
        return rv


def dataframe_to_dicts(df):
    """
    :param df: (pandas.DataFrame)
    :return: (list) a list of dicts, each for a row of the dataframe
    """
    return list(df.T.to_dict().values())


def tabular_format(rows):
    rowcount = 0
    columns = collections.defaultdict(list)
    columntypes = collections.defaultdict(set)
    for row in rows:
        rowcount += 1
        for ic, cell in enumerate(row):
            cell = numerify(str(cell))
            columns[ic].append(cell)
            columntypes[ic].add(type(cell))

    types = [str, float, int]
    for ic in range(len(columns)):
        type_ = str
        for type_ in types:
            if type_ in columntypes[ic]:
                break
        if type_ == float:
            columns[ic] = align.text_align_for_floats(columns[ic])
        if type_ == int:
            just_method = 'rjust'
        else:
            just_method = 'ljust'
        columns[ic] = align.text_equal_width(columns[ic], method=just_method)

    rows = []
    for ir in range(rowcount):
        row = []
        for ic in range(len(columns)):
            row.append(columns[ic][ir])
        rows.append(row)
    return rows


def _kvfmt(k, v, n, colon=':'):
    k = (k + colon).ljust(n)
    return '{}{}\n'.format(k, v)


def format_dictionary(d, bullet='*', colon=':'):
    n = max(len(k) for k in d) + 3
    parts = [bullet + _kvfmt(k, v, n, colon) for k, v in d.items()]
    return ''.join(parts)


def format_help_section(title, content):
    return title + ':\n' + format_dictionary(content, '  ', '') + '\n\n'
