#!/usr/bin/env python3

"""
Combined unit tests for the web package
"""

from dvk_archive.test.web.test_bs_connect import all_tests as test_bs
from dvk_archive.test.web.test_heavy_connect import all_tests as test_heavy

def test_all():
    """
    Run all web tests.
    """
    test_heavy()
    test_bs()
