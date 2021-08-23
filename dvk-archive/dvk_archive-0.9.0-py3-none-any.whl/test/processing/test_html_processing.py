#!/usr/bin/env/ python3

from dvk_archive.main.processing.html_processing import escape_to_char
from dvk_archive.main.processing.html_processing import replace_escapes
from dvk_archive.main.processing.html_processing import add_escapes
from dvk_archive.main.processing.html_processing import add_escapes_to_html
from dvk_archive.main.processing.html_processing import clean_element

def test_escape_to_char():
    """
    Tests the escape_to_char function.
    """
    # TEST REPLACING HTML ESCAPE CHARACTERS
    assert escape_to_char("&quot;") == "\""
    assert escape_to_char("&apos;") == "'"
    assert escape_to_char("&amp;") == "&"
    assert escape_to_char("&lt;") == "<"
    assert escape_to_char("&gt;") == ">"
    assert escape_to_char("&nbsp;") == " "
    assert escape_to_char("&#60;") == "<"
    assert escape_to_char("&#38;") == "&"
    # TEST NON-LATIN HTML ENTITIES
    assert escape_to_char("&Agrave;") == "À"
    assert escape_to_char("&Aacute;") == "Á"
    assert escape_to_char("&Auml;") == "Ä"
    assert escape_to_char("&Atilde;") == "Ã"
    assert escape_to_char("&Aring;") == "Å"
    # TEST REPLACING INVALID ESCAPE CHARACTERS
    assert escape_to_char(None) == ""
    assert escape_to_char("") == ""
    assert escape_to_char(" ") == ""
    assert escape_to_char("&;") == ""
    assert escape_to_char("&nope;") == ""
    assert escape_to_char("&#nope;") == ""
    assert escape_to_char("&#;") == ""

def test_replace_escapes():
    """
    Tests the replace_escapes function.
    """
    # TEST REPLACING HTML ESCAPE CHARACTERS IN STRING
    in_str = "&lt;i&gt;T&euml;st HTML&#60;&#47;i&#62;"
    assert replace_escapes(in_str) == "<i>Tëst HTML</i>"
    in_str = "this&that"
    assert replace_escapes(in_str) == "this&that"
    in_str = "remove&this;"
    assert replace_escapes(in_str) == "remove"
    # TEST REPLACING ESCAPE CHARACTERS IN INVALID TEST
    assert replace_escapes(None) == ""

def test_add_escapes():
    """
    Tests the add_escapes function.
    """
    # TEST REPLACING NON-STANDARD CHARACTERS WITH HTML ESCAPE CHARACTERS
    in_str = "<b>Fake tags.</b>"
    out_str = "&#60;b&#62;Fake tags&#46;&#60;&#47;b&#62;";
    assert add_escapes(in_str) == out_str
    in_str = "normal"
    assert add_escapes(in_str) == "normal"
    # TEST ADDING ESCAPE CHARACTERS TO INVALID STRING
    assert add_escapes(None) == ""

def test_add_escapes_to_html():
    """
    Tests the add_escapes_to_html function.
    """
    # TEST REPLACING CHARACTERS WITH HTML ESCAPE CHARACTERS IN HTML TEXT
    in_str = "<a href=\"Sommarfågel\">Sommarfågel</a>"
    out_str = "<a href=\"Sommarfågel\">Sommarf&#229;gel</a>"
    assert add_escapes_to_html(in_str) == out_str
    in_str = "<a href='Sommarfågel'>Sommarfågel</a>"
    out_str = "<a href='Sommarfågel'>Sommarf&#229;gel</a>"
    assert add_escapes_to_html(in_str) == out_str
    in_str = "<a href=\"Sommarfågel"
    out_str = "<a href=\"Sommarfågel"
    assert add_escapes_to_html(in_str) == out_str
    # TEST ADDING ESCAPE CHARACTERS TO INVALID STRING
    assert add_escapes_to_html(None) == ""

def test_clean_element():
    """
    Tests the clean_element function.
    """
    # TEST REMOVING LINE BREAKS IN ELEMENTS
    in_str = "<p> Start \r\n <b> \r Mid \n </b> \n\r End </p>"
    assert clean_element(in_str, False) == "<p> Start <b> Mid </b> End </p>"
    assert clean_element(in_str, True) == "Start <b> Mid </b> End"
    # TEST REMOVING WHITESPACE BETWEEN ELEMENT TAGS
    in_str = "<div>   Start  <i>  Mid     </i>   End     </div>"
    assert clean_element(in_str) == "<div> Start <i> Mid </i> End </div>"
    assert clean_element(in_str, True) == "Start <i> Mid </i> End"
    # TEST REMOVING WHITESPACE AT THE BEGINNING AND END OF THE GIVEN ELEMENT
    in_str = "     <span>Start<i>Mid</i>End</span> "
    assert clean_element(in_str) == "<span>Start<i>Mid</i>End</span>"
    assert clean_element(in_str, True) == "Start<i>Mid</i>End"
    # TEST REMOVING TAG ELEMENTS WHEN START AND/OR END TAGS ARE MISSING
    in_str = "A normal sentence."
    assert clean_element(in_str, True) == "A normal sentence."
    in_str = " Start <b> mid </b> End    "
    assert clean_element(in_str, True) == "Start <b> mid </b> End"
    in_str = " <p> Start <i> Mid </i> end  "
    assert clean_element(in_str, True) == "Start <i> Mid </i> end"
    in_str = "  start <b> mid </b> end </p>    "
    assert clean_element(in_str, True) == "start <b> mid </b> end"
    # TEST REMOVING TAG ELEMENTS WITH INVALID TAG
    in_str = "  < open   "
    assert clean_element(in_str, True) == "< open"
    in_str = "    open >  "
    assert clean_element(in_str, True) == "open >"
    in_str = "< single >"
    assert clean_element(in_str, True) == ""
    # TEST CLEANING AN INVALID HTML ELEMENT
    assert clean_element(None, True) == ""
    assert clean_element(None, False) == ""

def all_tests():
    """
    Runs all tests for the html_processing module.
    """
    test_escape_to_char()
    test_replace_escapes()
    test_add_escapes()
    test_add_escapes_to_html()
    test_clean_element()
