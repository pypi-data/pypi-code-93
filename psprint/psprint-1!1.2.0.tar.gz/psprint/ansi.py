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
ANSI colors' and styles' definitions
'''

import types
from pathlib import Path

import yaml

with open(Path(__file__).resolve().parent.joinpath("ansi.yml"), "r") as stream:
    ANSI = types.SimpleNamespace(**yaml.safe_load(stream))
    '''
    ANSI codes' namespace

    Earlier, these values were imported from
    `colorama. <https://pypi.org/project/colorama/>`__

    However, such import may not be needed.

    ANSI Colors:

      * 0: black, k
      * 1: red, r
      * 2: green, g
      * 3: yellow, y
      * 4: blue, b
      * 5: magenta, m
      * 6: cyan, c
      * 7: white, w
      * 8 + `code`: light `color name`, l`c`
      * 16: terminal, t  (Terminal-determined)

    ANSI Gloss:

      * 0: reset all
      * 1: normal
      * 2: dim
      * 3: bright

    '''
