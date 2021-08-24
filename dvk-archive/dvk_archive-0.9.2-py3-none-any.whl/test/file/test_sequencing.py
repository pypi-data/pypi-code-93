#!/usr/bin/env python3

from dvk_archive.main.file.dvk import Dvk
from dvk_archive.main.file.dvk_handler import DvkHandler
from dvk_archive.main.file.sequencing import get_sequence
from dvk_archive.main.file.sequencing import set_sequence
from dvk_archive.test.temp_dir import get_test_dir
from os.path import exists, join

def create_test_dvks() -> str:
    """
    Creates test DVK files for running sequencing tests.

    :return: Temp directory that DVK files are stored in
    :rtype: str
    """
    test_dir = get_test_dir()
    # Create unrelated single Dvk
    single = Dvk()
    single.set_dvk_file(join(test_dir, "single.dvk"))
    single.set_dvk_id("SNG01")
    single.set_title("Single")
    single.set_artist("Artist")
    single.set_page_url("/url/")
    single.set_media_file("media.txt")
    single.write_dvk()
    assert exists(single.get_dvk_file())
    # Create pair of Dvks to link as a sequence
    couple = Dvk()
    couple.set_dvk_file(join(test_dir,"couple1.dvk"))
    couple.set_dvk_id("CPL01")
    couple.set_title("Couple P1")
    couple.set_artist("Artist")
    couple.set_page_url("/url/")
    couple.set_media_file("media.jpg")
    couple.write_dvk()
    assert exists(couple.get_dvk_file())
    couple.set_dvk_file(join(test_dir,"couple2.dvk"))
    couple.set_dvk_id("CPL02")
    couple.set_title("Couple P2")
    couple.set_media_file("media.jpg")
    couple.write_dvk()
    assert exists(couple.get_dvk_file())
    # Create group of 3 Dvks to link as a sequence
    triple = Dvk()
    triple.set_dvk_file(join(test_dir,"triple1.dvk"))
    triple.set_dvk_id("TRI01")
    triple.set_title("Triple P1")
    triple.set_artist("Artist")
    triple.set_page_url("/url/")
    triple.set_media_file("media.png")
    triple.write_dvk()
    assert exists(triple.get_dvk_file())
    triple.set_dvk_file(join(test_dir,"triple2.dvk"))
    triple.set_dvk_id("TRI02")
    triple.set_title("Triple P2")
    triple.set_media_file("media.png")
    triple.write_dvk()
    assert exists(triple.get_dvk_file())
    triple.set_dvk_file(join(test_dir,"triple3.dvk"))
    triple.set_dvk_id("TRI03")
    triple.set_title("Triple P3")
    triple.set_media_file("media.png")
    triple.write_dvk()
    assert exists(triple.get_dvk_file())
    # Test that Dvks were written properly
    dvk_handler = DvkHandler(test_dir)
    dvk_handler.sort_dvks("a")
    assert dvk_handler.get_size() == 6
    assert dvk_handler.get_dvk(0).get_dvk_id() == "CPL01"
    assert dvk_handler.get_dvk(1).get_dvk_id() == "CPL02"
    assert dvk_handler.get_dvk(2).get_dvk_id() == "SNG01"
    assert dvk_handler.get_dvk(3).get_dvk_id() == "TRI01"
    assert dvk_handler.get_dvk(4).get_dvk_id() == "TRI02"
    assert dvk_handler.get_dvk(5).get_dvk_id() == "TRI03"
    return test_dir

def test_set_sequence():
    """
    Tests the set_sequence function.
    """
    # Set up test files
    test_dir = create_test_dvks()
    dvk_handler = DvkHandler(test_dir)
    dvk_handler.sort_dvks("a")
    assert dvk_handler.get_size() == 6
    # Test setting a sequence
    set_sequence(dvk_handler, [0,1])
    assert dvk_handler.get_dvk(0).get_dvk_id() == "CPL01"
    assert dvk_handler.get_dvk(0).is_first()
    assert dvk_handler.get_dvk(0).get_next_id() == "CPL02"
    assert dvk_handler.get_dvk(0).get_sequence_title() == ""
    assert dvk_handler.get_dvk(1).get_dvk_id() == "CPL02"
    assert dvk_handler.get_dvk(1).is_last()
    assert dvk_handler.get_dvk(1).get_prev_id() == "CPL01"
    assert dvk_handler.get_dvk(1).get_sequence_title() == ""
    # Test setting a sequence with sequence title
    set_sequence(dvk_handler, [3,4,5], "Title!")
    assert dvk_handler.get_dvk(3).get_dvk_id() == "TRI01"
    assert dvk_handler.get_dvk(3).is_first()
    assert dvk_handler.get_dvk(3).get_next_id() == "TRI02"
    assert dvk_handler.get_dvk(3).get_sequence_title() == "Title!"
    assert dvk_handler.get_dvk(4).get_dvk_id() == "TRI02"
    assert dvk_handler.get_dvk(4).get_prev_id() == "TRI01"
    assert dvk_handler.get_dvk(4).get_next_id() == "TRI03"
    assert dvk_handler.get_dvk(4).get_sequence_title() == "Title!"
    assert dvk_handler.get_dvk(5).get_dvk_id() == "TRI03"
    assert dvk_handler.get_dvk(5).is_last()
    assert dvk_handler.get_dvk(5).get_prev_id() == "TRI02"
    assert dvk_handler.get_dvk(5).get_sequence_title() == "Title!"
    # Test setting a single standalone Dvk file
    set_sequence(dvk_handler, [2], "Other")
    assert dvk_handler.get_dvk(2).get_dvk_id() == "SNG01"
    assert dvk_handler.get_dvk(2).is_first()
    assert dvk_handler.get_dvk(2).is_last()
    assert dvk_handler.get_dvk(2).get_sequence_title() == ""
    # Test that sequence data was written to disk
    dvk_handler = None
    dvk_handler = DvkHandler(test_dir)
    dvk_handler.sort_dvks("a")
    assert dvk_handler.get_dvk(0).get_next_id() == "CPL02"
    assert dvk_handler.get_dvk(1).get_prev_id() == "CPL01"
    assert dvk_handler.get_dvk(2).is_first()
    assert dvk_handler.get_dvk(3).get_next_id() == "TRI02"
    assert dvk_handler.get_dvk(4).get_next_id() == "TRI03"
    assert dvk_handler.get_dvk(5).get_prev_id() == "TRI02"
    # Test setting a sequence with invalid parameters
    set_sequence(None, [2])
    set_sequence(dvk_handler, None)
    set_sequence(dvk_handler, [])
    set_sequence()
    assert dvk_handler.get_dvk(0).get_next_id() == "CPL02"
    assert dvk_handler.get_dvk(1).get_prev_id() == "CPL01"
    assert dvk_handler.get_dvk(2).is_first()
    assert dvk_handler.get_dvk(3).get_next_id() == "TRI02"
    assert dvk_handler.get_dvk(4).get_next_id() == "TRI03"
    assert dvk_handler.get_dvk(5).get_prev_id() == "TRI02"

def test_get_sequence():
    """
    Tests the get_sequence method.
    """
    # Set up test files
    test_dir = create_test_dvks()
    dvk_handler = DvkHandler(test_dir)
    dvk_handler.sort_dvks("a")
    assert dvk_handler.get_size() == 6
    # Test getting sequence
    set_sequence(dvk_handler, [3,4,5])
    assert get_sequence(dvk_handler, 3) == [3,4,5]
    assert get_sequence(dvk_handler, 4) == [3,4,5]
    assert get_sequence(dvk_handler, 5) == [3,4,5]
    # Test getting sequence that forms a loop
    couple = dvk_handler.get_dvk(0)
    assert couple.get_dvk_id() == "CPL01"
    couple.set_prev_id("CPL02")
    couple.set_next_id("CPL02")
    couple.write_dvk()
    couple = dvk_handler.get_dvk(1)
    assert couple.get_dvk_id() == "CPL02"
    couple.set_prev_id("CPL01")
    couple.set_next_id("CPL01")
    couple.write_dvk()
    dvk_handler = DvkHandler(test_dir)
    dvk_handler.sort_dvks("a")
    assert get_sequence(dvk_handler, 0) == [0,1,0,1,0]
    assert get_sequence(dvk_handler, 1) == [1,0,1,0,1]
    # Test getting sequence from a single Dvk
    assert get_sequence(dvk_handler, 2) == [2]
    # Test getting sequence with invalid parameters
    assert get_sequence(dvk_handler, 6) == []
    assert get_sequence(dvk_handler, -1) == []
    assert get_sequence(dvk_handler, None) == []
    assert get_sequence(None, 2) == []
    assert get_sequence() == []

def all_tests():
    """
    Runs all tests for the sequencing.py module.
    """
    test_set_sequence()
    test_get_sequence()
