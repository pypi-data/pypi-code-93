#!/usr/bin/env python3

"""
Combined unit tests for the processing package
"""

from dvk_archive.test.processing.test_html_processing import all_tests as test_html
from dvk_archive.test.processing.test_list_processing import all_tests as test_list
from dvk_archive.test.processing.test_string_processing import all_tests as test_string
from dvk_archive.test.processing.test_string_compare import all_tests as test_compare


def test_all():
    """
    Run all processing tests.
    """
    test_html()
    test_list()
    test_string()
    test_compare()
    
