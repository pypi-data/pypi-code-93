#!/usr/bin/env python3

from dvk_archive.test.error_finding.test_same_ids import all_tests as same_ids
from dvk_archive.test.error_finding.test_missing_media import all_tests as missing
from dvk_archive.test.error_finding.test_unlinked_media import all_tests as unlinked

"""
Combined unit tests for the error_finding package
"""

def test_all():
    """
    Runs all error_finding tests.
    """
    same_ids()
    unlinked()
    missing()
