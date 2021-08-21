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
import sys
from os.path import abspath, join, dirname
import pytest
import os

# Make sure apav path is available
this_path = abspath(dirname(__file__))
# sys.path.append(join(this_path, "../.."))
# tests_dir = join(this_path, "../..", "apav", "tests")

def run_tests():
    os.chdir(this_path)
    pytest.main()
