#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020, 2021 Pradyumna Paranjape
# This file is part of psprint.
#
# psprint is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Test psfmt
"""

import unittest

from psprint import DEFAULT_PRINT

DEFAULT_PRINT.switches['disabled'] = False
DEFAULT_PRINT.switches['short'] = False
DEFAULT_PRINT.switches['pad'] = False
DEFAULT_PRINT.switches['bland'] = True
psfmt = DEFAULT_PRINT.psfmt


class MyFmtClass():
    """My Test Class with format string"""
    def __init__(self):
        self.attr = 'data'

    def __repr__(self) -> str:
        return f'data: {self.attr!s}'

    def __format__(self, spec):
        fmt_out = []
        for line_no, line in enumerate(self.__repr__().split("\n")):
            if line_no == 0:
                fmt_out.extend(psfmt(line, mark=spec))
            else:
                fmt_out.extend(psfmt(line, mark='cont'))
        return '\n'.join(fmt_out)

    def update(self, data: str, /):
        self.attr = data


class TestFmtStr(unittest.TestCase):
    def setUp(self):
        self.fmtobj = MyFmtClass()

    def test_one_word(self):
        self.assertEqual(f'{self.fmtobj:list}', '[LIST]data: data')

    def test_one_line(self):
        data = 'The Quick Brown Fox Jumps Over The Lazy Dog'
        self.fmtobj.update(data)
        self.assertEqual(f'{self.fmtobj:list}', f'[LIST]data: {data}')

    def test_multi_line(self):
        data = ['The Quick Brown Fox', 'Jumps Over', 'The Lazy Dog']
        expected_out_str = '[LIST]data: ' + '\n'.join(data)
        self.fmtobj.update('\n'.join(data))
        self.assertEqual(f'{self.fmtobj:list}', expected_out_str)


class testFmt(unittest.TestCase):
    def setUp(self):
        self.data = ['The quick brown', 'Fox jumps over', 'The lazy dog']

    def test_disabled(self):
        fstr = psfmt(*self.data, disabled=True)
        self.assertEqual(fstr, self.data)

    def test_join(self):
        fstr = psfmt(*self.data, disabled=True, sep='\t')
        self.assertEqual(fstr, '\t'.join(self.data))

    def test_w_sep(self):
        fstr = psfmt(*self.data, sep='\n')
        self.assertEqual(fstr, '\n'.join(self.data))

    def test_wo_sep(self):
        fstr = psfmt(*self.data)
        self.assertEqual(fstr, self.data)

    def test_empty_sep(self):
        fstr = psfmt(*self.data, sep='')
        self.assertEqual(fstr, ''.join(self.data))
