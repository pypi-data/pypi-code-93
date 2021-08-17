#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import joker.textmanip
from joker.textmanip import path


def _chk(func, argument, expectation):
    rv = func(argument)
    assert expectation == rv, rv


def test():
    assert joker.textmanip.remove_whitespaces('Sun Moon ') == 'SunMoon'

    a = 'No fear. \nNo distractions.\0'
    b = 'No fear. No distractions.'
    assert joker.textmanip.remove_control_chars(a) == b

    a = 'unix/filename\n'
    b = 'unixfilename\n'
    assert path.unix_filename_safe(a) == b, a

    s = r'windows*/\filename?'
    t = 'windows___filename_'
    r = path.windows_filename_safe(s)
    assert t == r, r

    _chk(path.windows_filename_safe, 'CON', 'CON_')

    a = 'textmanip'
    b = 'exmnp'
    assert joker.textmanip.remove_chars(a, 'tai') == b
    assert joker.textmanip.remove_chars(a, list('tai')) == b


if __name__ == '__main__':
    test()
