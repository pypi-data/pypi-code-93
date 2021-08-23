#!/usr/bin/env python3

from dvk_archive.main.file.dvk import Dvk
from dvk_archive.test.temp_dir import get_test_dir
from os import mkdir
from os.path import abspath, join

def create_test_files() -> str:
    """
    Creates files for testing error finding functions.

    :return: Path of the directory that holds test files
    :type: str
    """
    # CREATE TEST DIRECTORIES
    test_dir = get_test_dir()
    no_dvks = abspath(join(test_dir, "no_dvks"))
    main_sub = abspath(join(test_dir, "main_sub"))
    mkdir(no_dvks)
    mkdir(main_sub)
    # CREATE UNLINKED FILES
    with open(abspath(join(test_dir, "unlinked_main.txt")), "w") as out_file:
        out_file.write("MAIN")
    with open(abspath(join(main_sub, "unlinked_sub.png")), "w") as out_file:
        out_file.write("SUB")
    with open(abspath(join(no_dvks, "unlinked_no_dvk.jpg")), "w") as out_file:
        out_file.write("NO DVK")
    # CREATE MEDIA FILES TO BE LINKED BY DVK FILES
    with open(abspath(join(test_dir, "valid_media.png")), "w") as out_file:
        out_file.write("VALID")
    with open(abspath(join(test_dir, "mm_second.txt")), "w") as out_file:
        out_file.write("MISSING SECOND")
    with open(abspath(join(main_sub, "valid_second.png")), "w") as out_file:
        out_file.write("VALID SECOND")
    with open(abspath(join(main_sub, "linked.txt")), "w") as out_file:
        out_file.write("LINKED")
    # CREATE DVKS IN THE MAIN DIRECTORY
    missing_media_dvk = Dvk()
    missing_media_dvk.set_dvk_file(join(test_dir, "mm.dvk"))
    missing_media_dvk.set_dvk_id("MM123")
    missing_media_dvk.set_title("Missing Media")
    missing_media_dvk.set_artist("artist")
    missing_media_dvk.set_page_url("/url/")
    missing_media_dvk.set_media_file("unlinked_sub.png")
    missing_media_dvk.write_dvk()
    valid_media_dvk = Dvk()
    valid_media_dvk.set_dvk_file(join(test_dir, "valid_media.dvk"))
    valid_media_dvk.set_dvk_id("VAL123")
    valid_media_dvk.set_title("Valid")
    valid_media_dvk.set_artist("artist")
    valid_media_dvk.set_page_url("/url/")
    valid_media_dvk.set_media_file("valid_media.png")
    valid_media_dvk.write_dvk()
    multi_media_dvk = Dvk()
    multi_media_dvk.set_dvk_file(join(test_dir, "multi_media.dvk"))
    multi_media_dvk.set_dvk_id("VAL123")
    multi_media_dvk.set_title("All Media Valid")
    multi_media_dvk.set_artist("artist")
    multi_media_dvk.set_page_url("/url/")
    multi_media_dvk.set_media_file("valid_media.png")
    multi_media_dvk.set_secondary_file("mm_second.txt")
    multi_media_dvk.write_dvk()
    # CREATE DVKS IN THE SUB DIRECTORY
    missing_second_dvk = Dvk()
    missing_second_dvk.set_dvk_file(join(main_sub, "ms.dvk"))
    missing_second_dvk.set_dvk_id("MM123")
    missing_second_dvk.set_title("Missing Secondary")
    missing_second_dvk.set_artist("artist")
    missing_second_dvk.set_page_url("/url/")
    missing_second_dvk.set_media_file("linked.txt")
    missing_second_dvk.set_secondary_file("non-existant.png")
    missing_second_dvk.write_dvk()
    valid_second_dvk = Dvk()
    valid_second_dvk.set_dvk_file(join(main_sub, "valid_second.dvk"))
    valid_second_dvk.set_dvk_id("UNI246")
    valid_second_dvk.set_title("Valid Secondary")
    valid_second_dvk.set_artist("artist")
    valid_second_dvk.set_page_url("/url/")
    valid_second_dvk.set_media_file("non-existant.txt")
    valid_second_dvk.set_secondary_file("valid_second.png")
    valid_second_dvk.write_dvk()
    return test_dir
