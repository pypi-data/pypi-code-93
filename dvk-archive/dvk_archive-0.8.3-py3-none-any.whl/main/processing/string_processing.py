#!/usr/bin/env python3

from math import floor
from os.path import abspath

def pad_num(num:str=None, length:int=0) -> str:
    """
    Returns a String for a given String of a given length.
    If too small, pads out String with zeros.

    :param input: Number string to extend, defaults to None
    :type input: str, optional
    :param length: Length of returned String
    :type length: int, optional
    :return: Padded string
    :rtype: str
    """
    # RETURNS AN EMPTY STRING IF THE GIVEN STRING OR LENGTH IS INVALID
    if num is None or length < 1:
        return ""
    # RETURN STRING OF ZEROS IF LENGTH IS LESS THAN LENTH OF INPUT
    if length < len(num):
        return pad_num("0", length)
    # PAD OUT THE STRING WITH ZEROS TO REACH THE GIVEN STRING LENGTH
    new_num = num
    while len(new_num) < length:
        new_num = "0" + new_num
    return new_num

def remove_whitespace(text:str=None) -> str:
    """
    Removes the whitespace at the beginning and end of a given String.

    :param text: Given string, defaults to None
    :type text: str, optional
    :return: String without whitespace
    :rtype: str
    """
    # RETURN AN EMPTY STRING IF THE GIVEN STRING IS INVALID
    if text is None:
        return ""
    # FIND WHERE TEXT BEGINS AND ENDS
    start = 0
    while start < len(text) and (text[start] == " " or text[start] == "\t"):
        start = start + 1
    end = len(text) - 1
    while end > -1 and (text[end] == " " or text[end] == "\t"):
        end = end - 1
    end = end + 1
    # IF END < START, ASSUME THER'S NO WHITESPACE AT THE END
    if end < start:
        return text[start:len(text)]
    # RETURN TEXT SUBSTRING
    return text[start:end]

def truncate_string(text:str=None, length:int=90) -> str:
    """
    Shortens a given string to be at or below a given length.
    Attempts to keep readable by removing characters at break-points.

    :param text: Given string, defaults to None
    :type text: str, optional
    :param length: Maximum length of the returned string, defaults to None
    :type length: str, optional
    :return: Shortened string
    :rtype: str
    """
    # RETURN AN EMPTY STRING IF GIVEN STRING IS NONE OR EMPTY
    if text is None or length < 1:
        return ""
    # RETURN GIVEN STRING IF IT'S LENGTH IS <= THE VARIABLE LENGTH
    if len(text) <= length:
        return text
    # FIND INDEX TO START REMOVING CHARACTERS FROM.
    # ATTEMPTS TO BREAK AT A SPACE OR HYPHEN
    if " " in text:
        index = text.rfind(" ")
    elif "-" in text:
        index = text.rfind("-")
    else:
        index = floor(len(text)/2)
    # DELETE CHARACTERS FROM THE INDEX POSITION
    out = text
    if index < len(out) - index:
        index = index + 1
        while index < len(out) and length < len(out):
            out = out[:index] + out[index+1:]
    else:
        index = index - 1;
        while index > -1 and len(out) > length:
            out = out[:index] + out[index+1:]
            index = index - 1
        if (index > -1
                and index < len(out) -1
                and out[index] == out[index+1]
                and (out[index] == " " or out[index] == "-")):
            out = out[:index] + out[index+1:]
    # IF STILL TOO LONG, REMOVE CHARACTERS FROM THE END OF THE STRING
    if len(out) > length:
        out = out[:length]
    # REMOVE START AND END SPACERS
    while len(out) > 0 and (out[0] == " " or out[0] == "-"):
        out = out[1:]
    while len(out) > 0 and (out[len(out)-1] == " " or out[len(out)-1] == "-"):
        out = out[:-1]
    return out

def get_filename(text:str=None, length:int=90) -> str:
    """
    Returns a version of a given String that is safe for use as a filename.

    :param text: Given string, defaults to None
    :type text: str, optional
    :param length: Maximum length of the returned filename, defaults to 90
    :type length: int, optional
    :return: Filename
    :rtype: str
    """
    # IF GIVEN STRING IS NULL, RETURN STRING "0"
    if text is None:
        return "0"
    # REMOVE ALL NON-LETTER, NON-NUMERIC CHARACTERS
    i = 0
    out = ""
    while i < len(text):
        value = ord(text[i])
        if ((value > 47 and value < 58)
                or (value > 64 and value < 91)
                or (value > 96 and value < 123)
                or value == 32):
            out = out + text[i]
        elif value > 191 and value < 198:
            # REPLACE "A" VARIENTS
            out = out + "A"
        elif value > 199 and value < 204:
            # REPLACE "E" VARIENTS
            out = out + "E"
        elif value > 203 and value < 208:
            # REPLACE "I" VARIENTS
            out = out + "I"
        elif value == 209:
            # REPLACE "N" VARIENT
            out = out + "N"
        elif value > 209 and value < 215:
            # REPLACE "O" VARIENTS
            out = out + "O"
        elif value > 216 and value < 221:
            # REPLACE "U" VARIENTS
            out = out + "U"
        elif value == 221:
            # REPLACE "Y" VARIENT
            out = out + "Y"
        elif value > 223 and value < 230:
            # REPLACE "a" VARIENTS
            out = out + "a"
        elif value > 231 and value < 236:
            # REPLACE "e" VARIENTS
            out = out + "e"
        elif value > 235 and value < 240:
            # REPLACE "i" VARIENTS
            out = out + "i"
        elif value == 241:
            # REPLACE "n" VARIENT
            out = out + "n"
        elif value > 241 and value < 247:
            # REPLACE "o" VARIENTS
            out = out + "o"
        elif value > 248 and value < 253:
            # REPLACE "u" VARIENTS
            out = out + "u"
        elif value == 253 or value == 255:
            # REPLACE "y" VARIENTS
            out = out + "y"
        else:
            out = out + "-"
        # INCREMENT COUNTER
        i = i + 1
    # REMOVE START AND END SPACERS
    while len(out) > 0 and (out[0] == " " or out[0] == "-"):
        out = out[1:]
    while len(out) > 0 and (out[-1] == " " or out[-1] == "-"):
        out = out[:-1]
    # REMOVE DUPLICATE SPACERS
    i = 1
    while i < len(out):
        if (out[i] == " " or out[i] == "-") and out[i] == out[i-1]:
            out = out[:i] + out[i+1:]
            i = i - 1
        # INCREMENT COUNTER
        i = i + 1
    # REMOVE HANGING HYPHENS
    i = 1
    while i < (len(out) - 1):
        if out[i] == "-":
            if ((out[i-1] == " " and not out[i+1] == " ")
                    or (not out[i-1] == " " and out[i+1] == " ")):
                out = out[:i] + out[i+1:]
                i = i - 1
        # INCREMENT COUNTER
        i = i + 1
    # TRUNCATE STRING
    if length != -1:
        out = truncate_string(out, length)
    # RETURN CLEANED STRING
    if len(out) == 0:
        # IF FINAL STRING HAS NO LENGTH, RETURN STRING "0"
        return "0"
    return out

def get_extension(filename:str=None) -> str:
    """
    Returns the extension for a given filename or direct file URL.
    If extension does not exist, returns empty.

    :param filename: Given filename, defaults to None
    :type filename: str, optional
    :return: Extension for the filename
    :rtype: str
    """
    # RETURNS AN EMPTY STRING IF THE FILENAME IS NULL
    if filename is None:
        return ""
    # IF URL HAS A TOKEN MAKED BY A '?', REMOVE THE TOKEN
    end = filename.rfind("?")
    if end == -1:
        end = len(filename)
    # GET TEXT INCLUDING AND PROCEDING THE FINAL '.'
    start = filename.rfind(".", 0, end)
    if start == -1 or end - start > 6:
        # RETURNS EMPTY STRING IF TEXT IS TOO LONG/SHORT
        return ""
    # RETURN EXTENSION
    return filename[start:end]

def get_url_directory(url:str=None) -> str:
    """
    Returns the last sub-directory for a given URL.

    :param url: Given URL, defaults to None
    :type url: str, optional
    :return: Last sub-directory of the given URL
    :rtype: str
    """
    # RETURN EMPTY STRING IF URL IS INVALID
    if url is None:
        return ""
    # REMOVE LAST FORWARD SLASH FROM THE URL
    sub = url
    while len(sub) > 0 and sub[len(sub) - 1] == "/":
        sub = sub[:-1]
    # GET LAST SUB-DIRECTORY
    last = sub.rfind("/") + 1
    return sub[last:]

def truncate_path(parent:str=None, file:str=None) -> str:
    # RETURN EMPTY STRING IF FILE IS INVALID
    if file is None:
        return ""
    # RETURN FILE IF PARENT PATH IS INVALID
    if parent is None:
        return file
    # RETURN FILE IF PARENT IS NOT ACTUALLY A PARENT DIRECTORY
    full_parent = abspath(parent)
    full_file = abspath(file)
    if (full_parent == full_file
            or not full_file.startswith(full_parent)):
        return full_file
    # TRUNCATE THE FILE PATH OF THE GIVEN FILE
    truncated = full_file[len(full_parent):]
    return "..." + truncated
