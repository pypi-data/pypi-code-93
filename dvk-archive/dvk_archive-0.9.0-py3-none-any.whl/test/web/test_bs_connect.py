#!/usr/bin/env/ python3

from os import stat
from os.path import abspath, exists, join
from dvk_archive.test.temp_dir import get_test_dir
from dvk_archive.main.web.bs_connect import bs_connect
from dvk_archive.main.web.bs_connect import basic_connect
from dvk_archive.main.web.bs_connect import download
from dvk_archive.main.web.bs_connect import get_default_headers
from dvk_archive.main.web.bs_connect import get_direct_response
from dvk_archive.main.web.bs_connect import get_last_modified
from dvk_archive.main.web.bs_connect import json_connect

def test_get_direct_response():
    """
    Tests the get_direct_response function.
    """
    # TEST GETTING RESPONSE HEADERS
    url = "http://pythonscraping.com/exercises/exercise1.html"
    response = get_direct_response(url, get_default_headers())
    headers = response.headers
    assert headers["Server"] == "Apache"
    assert headers["Connection"] == "Keep-Alive"
    # TEST GETTING RESPONSE USING INVALID PARAMETERS
    assert get_direct_response() is None
    assert get_direct_response(None) is None
    assert get_direct_response("") is None
    assert get_direct_response("asdfghjkl") is None

def test_basic_connect():
    """
    Tests the basic_connect function
    """
    # TEST GETTING HTML PAGE
    url = "http://pythonscraping.com/exercises/exercise1.html"
    html = basic_connect(url)
    assert html is not None
    assert html.startswith("<html>\n<head>\n<title>A Useful Page</title>")
    # TEST GETTING INVALID HTML PAGE
    assert basic_connect() is None
    assert basic_connect(None) is None
    assert basic_connect("") is None
    assert basic_connect("asdfghjkl") is None

def test_bs_connect():
    """
    Tests the bs_connect function.
    """
    # TEST GETTING BEAUTIFULSOUP FROM PAGE
    url = "http://pythonscraping.com/exercises/exercise1.html"
    bs = bs_connect(url)
    assert bs is not None
    assert bs.find("h1").get_text() == "An Interesting Title"
    assert bs.find("title").get_text() == "A Useful Page"
    # TEST GETTING INVALID PAGE
    assert bs_connect() is None
    assert bs_connect(None) is None
    assert bs_connect("") is None
    assert bs_connect("qwertyuiop") is None

def test_json_connect():
    """
    Tests the json_connect function.
    """
    # TEST LOADING PAGE AS A JSON OBJECT
    json = json_connect("http://echo.jsontest.com/key/value/json/test")
    assert json["json"] == "test"
    assert json["key"] == "value"
    # TEST LOADING AN INVALID PAGE
    json = json_connect("asdfghjkl")
    assert json is None
    json = json_connect(None)
    assert json is None

def test_download():
    """
    Tests the download function.
    """
    # TEST DOWNLOADING A GIVEN FILE
    test_dir = get_test_dir()
    file = abspath(join(test_dir, "image.jpg"))
    url = "http://www.pythonscraping.com/img/gifts/img6.jpg"
    download(url, file)
    assert exists(file)
    assert stat(file).st_size == 39785
    # TEST DOWNLOADING WITH INVALID PARAMETERS
    file = join(test_dir, "invalid.jpg")
    download(None, None)
    assert not exists(file)
    download(None, file)
    assert not exists(file)
    download("asdfasdf", file)
    assert not exists(file)
    download(url, None)
    assert not exists(file)

def test_get_last_modified():
    """
    Tests the get_last_modified function.
    """
    d = {"Last-Modified": "Udf, 10 Jan 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/01/10|12:05"
    d = {"Last-Modified": "Udf, 23 Feb 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/02/23|20:23"
    d = {"Last-Modified": "Udf, 01 Mar 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/03/01|12:00"
    d = {"Last-Modified": "Udf, 10 Apr 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/04/10|12:05"
    d = {"Last-Modified": "Udf, 23 May 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/05/23|20:23"
    d = {"Last-Modified": "Udf, 01 Jun 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/06/01|12:00"
    d = {"Last-Modified": "Udf, 10 Jul 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/07/10|12:05"
    d = {"Last-Modified": "Udf, 23 Aug 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/08/23|20:23"
    d = {"Last-Modified": "Udf, 01 Sep 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/09/01|12:00"
    d = {"Last-Modified": "Udf, 10 Oct 2010 12:05:55 GMT"}
    assert get_last_modified(d) == "2010/10/10|12:05"
    d = {"Last-Modified": "Udf, 23 Nov 2015 20:23:55 GMT"}
    assert get_last_modified(d) == "2015/11/23|20:23"
    d = {"Last-Modified": "Udf, 01 Dec 2019 12:00:55 GMT"}
    assert get_last_modified(d) == "2019/12/01|12:00"
    # TEST INVALID TIMES
    d = {"Last-Modified": "Udf, 10 Nop 2010 12:05:55 GMT"}
    assert get_last_modified(d) == ""
    d = {"Last-Modified": "Mon, BB Aug FFFF GG:TT:PP GMT"}
    assert get_last_modified(d) == ""
    d = {"Last-Modified": ""}
    assert get_last_modified(d) == ""
    assert get_last_modified() == ""
    assert get_last_modified(dict()) == ""
    assert get_last_modified(None) == ""

def all_tests():
    """
    Runs all tests for the bs_connect module.
    """
    test_get_direct_response()
    test_basic_connect()
    test_bs_connect()
    test_json_connect()
    test_download()
    test_get_last_modified()
