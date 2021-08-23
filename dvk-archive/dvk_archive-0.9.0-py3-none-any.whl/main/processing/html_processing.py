#!/usr/bin/env python3

from dvk_archive.main.processing.string_processing import remove_whitespace
from html import unescape

def escape_to_char(escape:str=None) -> str:
    """
    Returns single character for a given HTML escape character.
    Returned in string format. Empty if escape is invalid.

    :param escape: HTML escape character, defaults to None
    :type escape: str, optional
    :return: Unicode escape character
    :rtype: str
    """
    # RETURNS GIVEN STRING IF GIVEN STRING IS NOT A VALID HTML ESCAPE CHARACTER
    if(escape is None
           or len(escape) < 3
           or not escape[0] == "&"
           or not escape[-1] == ";"):
        return ""
    replace = unescape(escape)
    if replace == escape:
        return ""
    return replace

def replace_escapes(text:str=None) -> str:
    """
    Replaces all HTML escape characters in a string with Unicode characters.

    :param text: Given string, defaults to None
    :type text: str, optional
    :return: String with HTML escape characters replaced
    :rtype: str
    """
    # RETURNS EMPTY STRING IF GIVEN STRING IS NONE
    if text is None:
        return ""
    # RUN WHILE STRING CONTAINS HTML ESCAPE CHARACTERS
    out = text
    start = out.find("&")
    while not start == -1:
        # GET AND CONVERT HTML ESCAPE CHARACTER
        end = out.find(";", start)
        if not end == -1:
            end = end + 1
            replaced = out[0:start]
            replaced = replaced + escape_to_char(out[start:end])
            replaced = replaced + out[end:len(out)]
            out = replaced
            start = out.find("&")
        else:
            start = -1
    return out

def add_escapes(text:str=None) -> str:
    """
    Replaces all uncommon characters in a String with HTML escapes.

    :param text: Given string, defaults to None
    :type text: str, optional
    :return: String with added HTML escape characters
    :rtype: str
    """
    # RETURNS AN EMPTY STRING IF THE GIVEN STRING IS NONE
    if text is None:
        return ""
    # RUN THROUGH EACH CHARACTER IN THE GIVEN STRING
    i = 0
    out = ""
    while i < len(text):
        value = ord(text[i])
        if ((value > 47 and value < 58)
                or (value > 64 and value < 91)
                or (value > 96 and value < 124)
                or value == ord(" ")):
            # IF CHARACTER IS ALPHA-NUMERIC, USE THE SAME CHARACTER
            out = out + text[i]
        else:
            # IF CHARACTER IS NOT ALPHA-NUMERIC, USE ESCAPE CHARACTER
            out = out + "&#" + str(value) + ";"
        # INCREMENT COUNTER
        i = i + 1
    return out

def add_escapes_to_html(text:str=None) -> str:
    """
    Replaces all uncommon characters in a String with HTML escapes.
    Keeps HTML tags and structures intact.

    :param text: Given HTML String, defaults to None
    :type text: str, optional
    :return: String with added HTML escape characters
    :rtype: str
    """
    # RETURNS EMPTY STRING IF THE GIVEN STRING IS NONE
    if text is None:
        return ""
    # RUN THROUGH EACH CHARACTER OF THE GIVEN STRING
    i = 0
    out = ""
    while i < len(text):
        value = ord(text[i])
        if value == 34 or value == 39:
            # LEAVE TEXT IN QUOTES ALONE
            end = text.find("\"", i + 1) + 1
            if end == 0:
                end = text.find("\'", i + 1) + 1
            if end == 0:
                end = len(text)
            out = out + text[i:end]
            i = end - 1
        elif value > 31 and value < 127:
            # LEAVE ALL LATIN AND HTML CHARACTERS ALONE
            out = out + text[i]
        else:
            # REPLACE NON-STANDARD CHARACTERS
            out = out + "&#" + str(value) + ";"
        # INCREMENT COUNTER
        i = i + 1
    # RETURN MODIFIED STRING
    return out

def clean_element(html:str=None, remove_ends:str=False) -> str:
    """
    Cleans up HTML element.
    Removes whitespace and removes header and footer tags.

    :param html: HTML element, defaults to None
    :type html: str, optional
    :param remove_ends: Whether to remove header and footer tags, defaults to None
    :type remove_ends: bool, optional
    :return: Cleaned HTML element
    :rtype: str
    """
    # RETURNS EMPTY STRING IF GIVEN ELEMENT IS NONE
    if html is None:
        return ""
    # REMOVE NEW LINE AND CARRIAGE RETURN CHARACTERS
    text = html.replace("\n", "")
    text = text.replace("\r", "")
    # REMOVE WHITESPACE BETWEEN TAGS
    while "  <" in text:
        text = text.replace("  <", " <")
    while ">  " in text:
        text = text.replace(">  ", "> ")
    # REMOVE HEADER AND FOOTER, IF SPECIFIED
    if remove_ends:
        text = remove_whitespace(text)
        # REMOVE HEADER
        if len(text) > 0 and text[0] == "<":
            start = text.find(">")
            if not start == -1:
                text = text[start + 1:len(text)]
        # REMOVE FOOTER
        if len(text) > 0 and text[-1] == ">":
            end = text.rfind("<")
            if not end == -1:
                text = text[0:end]
    # REMOVE WHITESPACE FROM THE START AND END OF STRING
    text = remove_whitespace(text)
    return text
