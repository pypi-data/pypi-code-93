"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""

import apav
import re
from apav.utils.hinting import *

# The version_str must always be literal due to how setup.py finds it
version_str = apav.__version__

_version_nums = re.compile(r"(\d+.\d+.\d+)")


def version_tuple() -> Tuple[int, ...]:
    """
    Get the major/minor/patch version number
    :return:
    """
    matches = re.findall(_version_nums, version_str)
    if len(matches) != 1:
        raise ValueError(f"Could not interpret version string: {version_str}")

    parts = matches[0].split(".")

    return tuple(int(i) for i in parts)
