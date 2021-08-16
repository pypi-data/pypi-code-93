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
# GNU Lesser General Public License for more details. #
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
'''
Information Marker

'''

import warnings
from typing import Dict, Union

from .ansi import ANSI
from .errors import ValueWarning
from .text_types import AnsiEffect, PrintPref

DEFAULT_STYLE: Dict[str, int] = {'color': 16, 'gloss': 1, 'bgcol': 16}
'''
Terminal-determined color, black background, normal gloss

'''


class InfoMark():
    '''
    Prefix Mark information

    Attributes:
        pref: PrintPref: Prefix text properties
        text: PrintText: Text properties

    Args:
        parent: Inherit information from-
        pref_max: pad prefix to reach length
        **kwargs:
            * pref: prefix string
            * pref_s: prefix short string
            * code:

                * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

            * for-

                * pref_color: color of of prefix
                * pref_gloss: gloss of prefix
                * pref_bgcol: background color of prefix
                * text_color: color of of text
                * text_gloss: gloss of text
                * text_bgcol: background color of text

    '''
    def __init__(self,
                 parent: 'InfoMark' = None,
                 pref_max: int = None,
                 **kwargs: Union[str, str]) -> None:
        if pref_max is None:
            pref_max = 7  # default

        # categorise kwargs
        pref_args = {}
        for key in DEFAULT_STYLE:
            if f'pref_{key}' in kwargs:
                pref_args[key] = kwargs[f'pref_{key}']
        text_args = {}
        for key in DEFAULT_STYLE:
            if f'text_{key}' in kwargs:
                text_args[key] = kwargs[f'text_{key}']

        # Determine prefixes
        for p_type in 'pref', 'pref_s':
            if kwargs.get(p_type) is not None:
                if isinstance(kwargs[p_type], (int, float)):
                    kwargs[p_type] = str(kwargs[p_type])
        pref = [kwargs.get('pref', ''), kwargs.get('pref_s', '>')]
        if pref[0] is not None and len(pref[0]) > pref_max:
            trim = pref[0][:pref_max]
            warnings.warn(f"Prefix string '{pref[0]}'" +
                          f" is too long (length>{pref_max}) " +
                          f"trimming to {trim}",
                          category=ValueWarning)
            pref[0] = trim
        if pref[1] is not None and len(pref[1]) > 1:
            trim = pref[1][:1]
            warnings.warn("Prefix string '{pref[1]}'" +
                          f" is too long (length>1) trimming to {trim}",
                          category=ValueWarning)
            pref[1] = trim
        parent_pref = parent.pref if parent else None
        parent_text = parent.text if parent else None

        self.pref = PrintPref(parent=parent_pref,
                              pref=pref,
                              pref_max=pref_max,
                              **pref_args)
        self.text = AnsiEffect(parent=parent_text, **text_args)

    def __repr__(self) -> str:
        '''
        String format of available information
        '''
        return "\t".join(
            (str(self.pref.style), self.pref.pref[0], self.pref.pref[1],
             self.text.style + "<CUSTOM>" + ANSI.RESET_ALL))

    def get_info(self) -> str:  # pragma: no cover
        '''
        Print information about ``InfoMark``

        '''
        info = str(self)
        print(info)
        return info
