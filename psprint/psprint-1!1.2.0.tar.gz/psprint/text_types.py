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
Text Parts

'''

from typing import List, Tuple, Union

from .ansi import ANSI
from .errors import BadBGCol, BadColor, BadGloss, BadPrefix, BadShortPrefix


class AnsiEffect():
    '''
    Plain text object
    Text to be printed to (ANSI) terminal

    Args:
        color: color of text [0-15]
        gloss: gloss of text {0: bland, 1:normal ,2: dim, 3: bright}
        bgcol: color of background [0-15]

    Attributes:
        color: color of text
        gloss: gloss of text
        bgcol: background color

    Raises:
        BadColor
        BadGloss
        BadBGCol

    '''
    def __init__(self,
                 parent=None,
                 color: str = None,
                 gloss: str = None,
                 bgcol: str = None) -> None:
        # inherit
        self.color, self.gloss, self.bgcol = self.inherit(parent)

        # modify
        try:
            self.color: str = ANSI.FG_COLORS[color] if color else self.color
        except KeyError:
            raise BadColor(color) from None
        try:
            self.gloss: str = ANSI.GLOSS[gloss] if gloss else self.gloss
        except KeyError:
            raise BadGloss(gloss) from None
        try:
            self.bgcol: str = ANSI.BG_COLORS[bgcol] if bgcol else self.bgcol
        except KeyError:
            raise BadBGCol(bgcol) from None

    @staticmethod
    def inherit(parent):
        '''
        object without parent
        set attributes to defaults
        '''
        if parent is None:
            return ANSI.FG_COLORS['t'], ANSI.GLOSS['n'], ANSI.BG_COLORS['t']
        return parent.color, parent.gloss, parent.bgcol

    @property
    def style(self) -> str:
        '''
        All style combined
        '''
        return self.color + self.bgcol + self.gloss

    def __str__(self) -> str:
        '''
        Human readable form
        '''
        return self.style

    def __repr__(self) -> str:  # pragma: no cover
        '''
        repr(self)
        '''
        return ' '.join((repr(self.color), repr(self.gloss), repr(self.bgcol)))


class PrintPref():
    '''
    Prefix that informs about Text

    Args:
        parent: template object for style
        pref: prefix in [long, short] format
        pref_max: pad with `space` to length
        **kwargs:
            * code:

                * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

            * for-

                * color: color of of prefix
                * gloss: gloss of prefix
                * bgcol: background color of prefix


    Arguments:
        pref: tuple: prefix long, short
        brackets: tuple: bool long, short
        pad: tuple: pad long, short
        style: AnsiEffect: color/gloss style

    Raises:
        BadPrefix
        BadShortPrefix

    '''
    def __init__(self,
                 parent=None,
                 pref: List[str] = None,
                 pref_max: int = 0,
                 **kwargs) -> None:
        self.brackets = [1, 1]
        style, self.pref = self._inherit(parent=parent, pref=pref)
        self.style = AnsiEffect(parent=style, **kwargs)
        # 0: long, 1: short
        pad_max = (pref_max, 1)
        pad_len: List[int] = [0, 0]
        for idx, pref_type in enumerate(self.pref):
            if not (isinstance(pref_type, str) or pref_type is None):
                raise (BadPrefix, BadShortPrefix)[idx](pref_type) from None
            if not pref_type:
                # pref_type is blank
                self.brackets[idx] = 0
                pad_len[idx] += 2  # corresponding to `[]`
            pad_len[idx] += max(pad_max[idx] - len(pref_type), 0)
        self.pad = [' ' * (span + 1) for span in pad_len]

    @staticmethod
    def _inherit(
            parent=None,
            pref: List[str] = None) -> Tuple[Union[AnsiEffect, None], list]:
        '''
        inherit pref and style from parent if not supplied
        '''
        if parent is None:
            return None, pref or ['', '']
        if pref is None:  # pragma: no cover
            # Logically never reached unless explicitly stated
            pref = [parent.pref[0], parent.pref[1]]
        pref[0] = pref[0] or parent.pref[0]
        pref[1] = pref[1] or parent.pref[1]
        return parent.style, pref

    def __len__(self) -> int:  # pragma: no cover
        '''
        length of prefix
        '''
        return len(self.pref[0])

    def to_str(self, **kwargs) -> str:
        '''
        Print prefix with style

        Args:
            short: prefix in short form?
            pad: Pad prefix
            bland: colorless pref
        '''
        pref_typ = int(kwargs.get('short', False))  # 1 if short, else 0
        parts = {
            'ansi': '' if kwargs.get('bland') else str(self.style),
            'text': self.pref[pref_typ],
            'brackets': self.brackets[pref_typ],
            'pref_pad': self.pad[pref_typ] if kwargs.get('pad') else '',
            'reset': '' if kwargs.get('bland') else ANSI.RESET_ALL,
        }
        return ''.join([
            parts['ansi'],
            '[' * parts['brackets'],
            parts['text'],
            ']' * parts['brackets'],
            parts['reset'],
            parts['pref_pad'],
        ])
