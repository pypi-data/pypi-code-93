import sys
from os.path import abspath, join, dirname
import pytest
import os

# Make sure apav path is available
this_path = abspath(dirname(__file__))
sys.path.append(join(this_path, "../.."))
tests_dir = join(this_path, "../..", "apav", "tests")

def run_tests():
    os.chdir(tests_dir)
    pytest.main()

