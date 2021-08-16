#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
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
'''
Errors and warnings
'''


class PSPrintError(Exception):
    '''
    Base error from PSPrint
    '''


class PSPrintWarning(Warning):
    '''
    Base warning category from PSPrint
    '''


class BadMark(PSPrintError):
    '''
    A ``mark`` supplied in ``config`` cannot be parsed

    Args:
        mark: passed mark
        config: config file that defined the mark
    '''
    def __init__(self, mark: str, config: str) -> None:
        super().__init__(f'''
        Prefix-mark {mark} from {config} couldn't be parsed
        ''')


class BadPref(Exception):
    '''
    Prefix Style declared incorrectly

    Args:
        key: key
        value: (Bad) value supplied

    '''
    def __init__(self, key, value):
        super().__init__(f'''
        Bad value {value} for {key}
        ''')


class BadStyle(Exception):
    '''
    Style declared incorrectly

    Args:
        key: key
        value: (Bad) value supplied

    '''
    def __init__(self, key, value):
        super().__init__(f'''
        Bad value {repr(value)} for style {key}
        ''')


class BadPrefix(BadPref):
    '''
    Prefix string Error

    '''
    def __init__(self, prefix):
        super().__init__('pref', prefix)


class BadShortPrefix(BadPref):
    '''
    Prefix short string Error

    '''
    def __init__(self, pref_s):
        super().__init__('pref_s', pref_s)


class BadColor(BadStyle):
    '''
    Color Error

    '''
    def __init__(self, color):
        super().__init__('color', color)


class BadGloss(BadStyle):
    '''
    Gloss Error

    '''
    def __init__(self, gloss):
        super().__init__('gloss', gloss)


class BadBGCol(BadStyle):
    '''
    Background Color Error

    '''
    def __init__(self, bgcol):
        super().__init__('bgcol', bgcol)


class KeyWarning(PSPrintWarning):
    '''
    Warning that a key was wrongly passed and has been interpreted as default
    '''


class ValueWarning(PSPrintWarning):
    '''
    Warning that a value was wrongly passed and has been interpreted as default
    '''
