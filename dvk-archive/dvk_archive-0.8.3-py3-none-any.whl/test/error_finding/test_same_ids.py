#!/usr/bin/env python3

from dvk_archive.main.error_finding.same_ids import get_same_ids
from dvk_archive.test.error_finding.error_files import create_test_files
from os import pardir
from os.path import abspath, basename, join

def test_get_same_ids():
    """
    Tests the get_same_ids function.
    """
    test_dir = create_test_files()
    # GET OTHER DIRECTORIES
    main_sub = abspath(join(test_dir, "main_sub"))
    no_dvks = abspath(join(test_dir, "no_dvks"))
    # TEST GETTING DVKS WITH THE SAME ID
    same = get_same_ids(test_dir)
    assert len(same) == 2
    assert len(same[0]) == 2
    assert basename(same[0][0]) == "multi_media.dvk"
    assert abspath(join(same[0][0], pardir)) == test_dir
    assert basename(same[0][1]) == "valid_media.dvk"
    assert abspath(join(same[0][1], pardir)) == test_dir
    assert len(same[1]) == 2
    assert basename(same[1][0]) == "mm.dvk"
    assert abspath(join(same[1][0], pardir)) == test_dir
    assert basename(same[1][1]) == "ms.dvk"
    assert abspath(join(same[1][1], pardir)) == main_sub
    # TEST GETTING DVKS WITH THE SAME ID IN DIRECTORY WITHOUT DVK FILES
    assert get_same_ids(no_dvks) == []
    # TEST GETTING SAME IDS IN INVALID DIRECTORIES
    assert get_same_ids("/non-existant/directory") == []
    assert get_same_ids(None) == []

def all_tests():
    """
    Runs all tests for the same_ids.py module.
    """
    test_get_same_ids()
