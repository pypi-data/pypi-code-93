#!/usr/bin/env/ python3

from dvk_archive.main.processing.list_processing import clean_list

def test_clean_list():
    """
    Tests the clean_list function.
    """
    # SET UP LIST
    lst = ["these"]
    lst.append("are")
    lst.append("things")
    lst.append("")
    lst.append(None)
    lst.append("are")
    # TEST CLEANING ARRAY
    lst = clean_list(lst)
    assert len(lst) == 4
    assert lst[0] == "these"
    assert lst[1] == "are"
    assert lst[2] == "things"
    assert lst[3] == ""
    # TEST CLEANING INVALID ARRAY
    lst = clean_list(None)
    assert len(lst) == 0

def all_tests():
    """
    Runs all tests for the list_processing module:
    """
    test_clean_list()
