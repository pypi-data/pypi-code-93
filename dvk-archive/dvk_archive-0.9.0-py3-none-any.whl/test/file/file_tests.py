#!/usr/bin/env python3

"""
Combined unit tests for the file package
"""

from dvk_archive.test.file.test_dvk import all_tests as test_dvk
from dvk_archive.test.file.test_dvk_handler import all_tests as test_handler
from dvk_archive.test.file.test_reformat import all_tests as test_reformat
from dvk_archive.test.file.test_rename import all_tests as test_rename


def test_all():
    """
    Runs all file tests.
    """
    test_handler()
    test_dvk()
    test_reformat()
    test_rename()
    
