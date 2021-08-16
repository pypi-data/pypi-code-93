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
'''
Prompt String-like Print
'''

import os
import sys

from .config import read_config
from .printer import PrintSpace


# Initiate default print function
def init_print(custom: os.PathLike = None) -> PrintSpace:
    '''
    Initiate ps-print function with default marks
    and marks read from various psprintrc configurarion files

    Args:
        custom: custom configuration file location

    '''

    default_print = read_config(custom)

    if 'idlelib.run' in sys.modules or not sys.stdout.isatty():
        # Running inside idle
        default_print.switches['bland'] = True

    return default_print


DEFAULT_PRINT = init_print()
'''
PrintSpace object created by reading defaults from various
psprintrc and psprint/style.yml files

'''

print = DEFAULT_PRINT.psprint
'''
psprint function for imports

'''

psfmt = DEFAULT_PRINT.psfmt
'''
ps formatting function for imports

'''

__all__ = ['DEFAULT_PRINT', 'print']

__version__ = '1!1.2.0'
