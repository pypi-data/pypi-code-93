#!/usr/bin/env python3

from dvk_archive.main.error_finding.unlinked_media import get_unlinked_media
from dvk_archive.test.error_finding.error_files import create_test_files
from os import pardir
from os.path import abspath, basename, join

def test_get_unlinked_media():
    """
    Tests the get_unlinked_media function.
    """
    test_dir = create_test_files()
    # GET OTHER DIRECTORIES
    main_sub = abspath(join(test_dir, "main_sub"))
    no_dvks = abspath(join(test_dir, "no_dvks"))
    # TEST GETTING UNLINKED FILES
    unlinked = get_unlinked_media(test_dir)
    assert len(unlinked) == 2
    assert basename(unlinked[0]) == "unlinked_main.txt"
    assert abspath(join(unlinked[0], pardir)) == test_dir
    assert basename(unlinked[1]) == "unlinked_sub.png"
    assert abspath(join(unlinked[1], pardir)) == main_sub
    # TEST THAT THERE ARE NO UNLINKED FILES IN THE NO_DVK TEST FOLDER
    unlinked = get_unlinked_media(no_dvks)
    assert len(unlinked) == 0
    # TEST GETTING UNLINKED FILES WITH INVALID DIRECTORIES
    assert get_unlinked_media("/non-existant/directory") == []
    assert get_unlinked_media(None) == []

def all_tests():
    """
    Runs all tests for the unlinked_media.py module.
    """
    test_get_unlinked_media()
