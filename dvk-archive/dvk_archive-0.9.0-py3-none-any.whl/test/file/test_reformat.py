#!/usr/bin/env python3

from dvk_archive.main.file.dvk import Dvk
from dvk_archive.main.file.dvk_handler import DvkHandler
from dvk_archive.main.file.reformat import reformat_dvks
from dvk_archive.main.web.bs_connect import download
from dvk_archive.test.temp_dir import get_test_dir
from os import pardir
from os.path import abspath, basename, exists, join

def test_reformat_dvks():
    """
    Tests the reformat_dvks function.
    """
    # WRITE DVK FILE THAT SHOULD NOT BE CHANGED WHEN REFORMATTED
    test_dir = get_test_dir()
    no_change_dvk = Dvk()
    no_change_dvk.set_dvk_file(join(test_dir, "no_change.dvk"))
    no_change_dvk.set_dvk_id("NOC123")
    no_change_dvk.set_title("No change")
    no_change_dvk.set_artist("NoChange")
    no_change_dvk.set_page_url("nochange/url/")
    no_change_dvk.set_media_file("no_change.txt")
    no_change_dvk.set_description("<b>keep description</b>")
    no_change_dvk.write_dvk()
    # WRITE DVK FILE THAT SHOULD HAVE DESCRIPTION AND MEDIA FILE ALTERED
    altered_dvk = Dvk()
    altered_dvk.set_dvk_file(join(test_dir, "desc.dvk"))
    altered_dvk.set_dvk_id("DES123")
    altered_dvk.set_title("Alter Description")
    altered_dvk.set_artist("DescArtist")
    altered_dvk.set_page_url("desc/url/")
    altered_dvk.set_media_file("desc.txt")
    download("http://www.pythonscraping.com/img/gifts/img6.jpg", altered_dvk.get_media_file())
    altered_dvk.set_description("  <b>   <i> Clean Description </i>   </b> ")
    altered_dvk.write_dvk()
    # CHECK THAT TEST FILES WERE WRITTEN PROPERLY
    assert exists(no_change_dvk.get_dvk_file())
    assert exists(altered_dvk.get_dvk_file())
    assert exists(altered_dvk.get_media_file())
    # REFORMAT DVK FILES
    dvk_handler = DvkHandler()
    dvk_handler.read_dvks(test_dir)
    dvk_handler.sort_dvks("a")
    reformat_dvks(dvk_handler)
    assert dvk_handler.get_size() == 2
    # TEST ALTERED_DVK FORMATTED PROPERLY
    assert dvk_handler.get_dvk(0).get_dvk_file() == altered_dvk.get_dvk_file()
    assert dvk_handler.get_dvk(0).get_dvk_id() == "DES123"
    assert dvk_handler.get_dvk(0).get_title() == "Alter Description"
    assert len(dvk_handler.get_dvk(0).get_artists()) == 1
    assert dvk_handler.get_dvk(0).get_artists()[0] == "DescArtist"
    assert dvk_handler.get_dvk(0).get_page_url() == "desc/url/"
    assert abspath(join(dvk_handler.get_dvk(0).get_dvk_file(), pardir)) == test_dir
    assert basename(dvk_handler.get_dvk(0).get_media_file()) == "desc.jpg"
    assert dvk_handler.get_dvk(0).get_description() == "<b> <i> Clean Description </i> </b>"
    # TEST FILES WERE ACTUALLY WRITTEN TO FILE
    dvk_handler.read_dvks(test_dir)
    dvk_handler.sort_dvks("a")
    assert abspath(join(dvk_handler.get_dvk(0).get_dvk_file(), pardir)) == test_dir
    assert basename(dvk_handler.get_dvk(0).get_media_file()) == "desc.jpg"
    assert dvk_handler.get_dvk(0).get_description() == "<b> <i> Clean Description </i> </b>"
    assert dvk_handler.get_dvk(1).get_dvk_file() == no_change_dvk.get_dvk_file()
    assert dvk_handler.get_dvk(1).get_dvk_id() == "NOC123"
    assert dvk_handler.get_dvk(1).get_title() == "No change"
    assert len(dvk_handler.get_dvk(1).get_artists()) == 1
    assert dvk_handler.get_dvk(1).get_artists()[0] == "NoChange"
    assert dvk_handler.get_dvk(1).get_page_url() == "nochange/url/"
    assert dvk_handler.get_dvk(1).get_media_file() == no_change_dvk.get_media_file()
    assert dvk_handler.get_dvk(1).get_description() == "<b>keep description</b>"
    # TEST WITH INVALID DVK HANDLER
    reformat_dvks()

def all_tests():
    """
    Runs all tests for the reformat.py module.
    """
    test_reformat_dvks()
