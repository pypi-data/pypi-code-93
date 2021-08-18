#!/usr/bin/env python3

from os import mkdir
from os.path import abspath, exists, join
from tempfile import gettempdir
from shutil import rmtree

def get_test_dir() -> str:
    """
    Creates and returns test directory.

    :return: File path of the test directory
    :rtype: str
    """
    test_dir = abspath(join(abspath(gettempdir()), "dvk_test"))
    if(exists(test_dir)):
        rmtree(test_dir)
    mkdir(test_dir)
    return test_dir
