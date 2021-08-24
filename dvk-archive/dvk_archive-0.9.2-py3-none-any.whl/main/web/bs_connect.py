#!/usr/bin/env python3

from bs4 import BeautifulSoup
from dvk_archive.main.processing.string_processing import pad_num
from io import BytesIO
from json import loads
from os.path import abspath, exists
from requests import exceptions
from requests import Response
from requests import Session
from shutil import copyfileobj
from urllib.error import HTTPError

def get_default_headers() -> dict:
    """
    Return headers to use when making a URL connection.
    """
    headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept-Language":
        "en-US,en;q=0.5"}
    return headers

def get_direct_response(url:str=None, headers:dict=None, data:dict=None) -> Response:
    # RETURN NONE IF URL IS INVALID
    if url is None or url == "":
        return None
    session = Session()
    try:
        # SEND REQUEST
        if data is None:
            # SEND GET REQUEST IF THERE IS NO POST DATA
            response = session.get(url, headers=headers)
        else:
            # SEND POST REQUEST IF POST DATA IS PROVIDED
            response = session.post(url, data=data)
        return response
    except:
        return None
    return None

def basic_connect(url:str=None, encoding:str="utf-8", data:dict=None) -> str:
    """
    Connects to a URL and returns the HTML source.
    Doesn't work with JavaScript

    :param url: URL to retrieve, defaults to None
    :type url: str, optional
    :param encoding: Text encoding to use, defaults to "utf-8"
    :type encoding: str, optional
    :param data: Request payload for post requests, defaults to None
    :type data: str, optional
    :return: HTML source
    :rtype: str
    """
    # RETURN NONE IF URL IS INVALID
    if url is None or url == "":
        return None
    try:
        # GET REQUEST
        response = get_direct_response(url, get_default_headers(), data)
        # SET ENCODING
        if encoding is None:
            response.encoding = request.apparent_encoding
        else:
            response.encoding = encoding
        return response.text
    except:
        return None

def bs_connect(url:str=None, encoding:str="utf-8", data:dict=None) -> BeautifulSoup:
    """
    Connects to a URL and returns a BeautifulSoup object.
    Doesn't work with JavaScript

    :param url: URL to retrieve, defaults to None
    :type url: str, optional
    :param encoding: Text encoding to use, defaults to "utf-8"
    :type encoding: str, optional
    :param data: Request payload for post requests, defaults to None
    :type data: str, optional
    :return: BeautifulSoup object of the URL page
    :rtype: str
    """
    html = basic_connect(url, encoding, data)
    if html is None or html == "":
        return None
    return BeautifulSoup(html, features="lxml")

def json_connect(url:str=None, encoding:str="utf-8", data:dict=None) -> dict:
    """
    Connects to a URL and returns a dict with JSON data.

    :param url: URL to retrieve, defaults to None
    :type url: str, optional
    :param encoding: Text encoding to use, defaults to "utf-8"
    :type encoding: str, optional
    :param data: Request payload for post requests, defaults to None
    :type data: str, optional
    :return: Dictionary with JSON data
    :rtype: dict
    """
    html = basic_connect(url, encoding, data)
    # RETURN NONE IF RETURNED DATA IS NONE OR INVALID
    if html is None or html == "":
        return None
    try:
        # CONVERT TO JSON
        json = loads(html)
        return json
    except:
        return None

def download(url:str=None, file_path:str=None) -> dict:
    """
    Downloads a file from given URL to given file.

    :param url: Given URL, defaults to None
    :type url: str, optional
    :param file_path: Given file path, defaults to None
    :type file_path: str, optional
    :return: Headers retrieved from the given media URL
    :rtype: dict
    """
    if (url is not None and file_path is not None):
        file = abspath(file_path)
        # SAVE FILE
        try:
            session = Session()
            headers = get_default_headers()
            response = session.get(url, headers=headers)
            byte_obj = BytesIO(response.content)
            byte_obj.seek(0)
            with open(file, "wb") as f:
                copyfileobj(byte_obj, f)
            return response.headers
        except (HTTPError,
                exceptions.ConnectionError,
                exceptions.MissingSchema,
                ConnectionResetError):
            print("Failed to download:" + url)
        return dict()

def get_last_modified(headers:dict=None) -> str:
    """
    Returns the time a webpage was last modified from its response headers.

    :param headers: HTML request headers, defaults to None
    :type headers: dict, optional
    :return: Last modified date and time in DVK time format
    :rtype: str
    """
    # RETURNS EMPTY STRING IF GIVEN HEADERS ARE INVALID
    if headers is None:
        return ""
    try:
        modified = headers["Last-Modified"]
    except KeyError:
        return ""
    # GET PUBLICATION TIME
    try:
        day = int(modified[5:7])
        month_str = modified[8:11].lower()
        year = int(modified[12:16])
        hour = int(modified[17:19])
        minute = int(modified[20:22])
        # GET MONTH
        months = [
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec"]
        month = 0
        while month < 12:
            if month_str == months[month]:
                break
            month += 1
        month += 1
        if month > 12:
            return ""
        time = pad_num(str(year), 4) + "/" + pad_num(str(month), 2) + "/"
        time = time + pad_num(str(day), 2) + "|" + pad_num(str(hour), 2)
        time = time + ":" + pad_num(str(minute), 2)
        return time
    except ValueError:
        # RETURNS EMPTY STRING IF GETTING TIME FAILS
        return ""
