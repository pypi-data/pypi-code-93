#!/usr/bin/env python3

from dvk_archive.main.error_finding.missing_media import get_missing_media_dvks
from dvk_archive.test.error_finding.error_files import create_test_files
from os import pardir
from os.path import abspath, basename, join

def test_get_missing_media_dvks():
    """
    Tests the get_missing_media_dvks function.
    """
    test_dir = create_test_files()
    # GET OTHER DIRECTORIES
    main_sub = abspath(join(test_dir, "main_sub"))
    no_dvks = abspath(join(test_dir, "no_dvks"))
    # TEST GETTING DVK FILES WITH INVALID OR MISSING LINKED MEDIA FILES
    missing = get_missing_media_dvks(test_dir)
    assert len(missing) == 3
    assert basename(missing[0]) == "mm.dvk"
    assert abspath(join(missing[0], pardir)) == test_dir
    assert basename(missing[1]) == "ms.dvk"
    assert abspath(join(missing[1], pardir)) == main_sub
    assert basename(missing[2]) == "valid_second.dvk"
    assert abspath(join(missing[2], pardir)) == main_sub
    # TEST GETTING MISSING MEDIA DVKS IN DIRECTORY WITH NO DVK FILES
    assert get_missing_media_dvks(no_dvks) == []
    # TEST GETTING MISSING MEDIA WITH INVALID DIRECTORIES
    assert get_missing_media_dvks("/non-existant/directory") == []
    assert get_missing_media_dvks(None) == []

def all_tests():
    """
    Runs all tests for the missing_media.py module.
    """
    test_get_missing_media_dvks()
