#!/usr/bin/env python3

def compare_strings(str1:str=None, str2:str=None) -> int:
    """
    Compares two strings alphabetically.
    Not case sensitive.

    :param str1: 1st string to compare, defaults to None
    :type str1: str, optional
    :param str2: 2nd string to compare, defaults to None
    :type str2: str, optional
    :return: String which should come first.
    :rtype: int
    """
    # RETURNS 0 IF EITHER STRING IS INVALID
    if str1 is None or str2 is None:
        return 0
    # RETURN WHICH STRING SHOULD COME FIRST
    sort = sorted([str1.upper(), str2.upper()])
    if sort[0] == sort[1]:
        return 0
    if sort[0] == str1.upper():
        return -1
    return 1

def is_digit(char_str:str=None) -> bool:
    """
    Return whether a single character string is a digit (0-9)

    :param char_str: String of a single character, defaults to None
    :type char_str: str, optional
    :return: Whether char_string is a digit
    :rtype: bool
    """
    # RETURN FALSE IF GIVEN CHARACTER IS INVALID
    if char_str is None or not len(char_str) == 1:
        return False
    # RETURN WHETHER GIVEN CHARACTER IS A DIGIT
    asc = ord(char_str)
    if asc > 47 and asc < 58:
        return True
    return False

def is_number_string(input_str:str=None) -> bool:
    """
    Return whether a given string starts with numerical information.
    Returns True if first character is a digit or a decimal point/comma.

    :param input_str: Given string, default to None
    :type input_str: str, optional
    :return: Whether input_string starts with numerical information
    :rtype: bool
    """
    # RETURNS FALSE IF GIVEN STRING IS INVALID
    if input_str is None or len(input_str) < 1:
        return False
    # RETURN WHETHER STRING STARTS WITH NUMERICAL INFORMATION
    start_char = input_str[0]
    if len(input_str) > 1 and is_digit(input_str[1]):
        if start_char == "." or start_char == ",":
            return True
    return is_digit(start_char)

def get_section(input_str:str=None) -> str:
    """
    Return the first section from a given string.
    Section will contain either only string data or numerical data.

    :param input_str: Given string, defaults to None
    :type input_str: str, optional
    :return: First section of the given string
    :rtype: str
    """
    # RETURNS EMPTY STRING IF GIVEN STRING IS INVALID
    if input_str is None or input_str == "":
        return ""
    # RETURN THE FIRST SECTION
    end = 1
    is_num = is_number_string(input_str)
    while (end < len(input_str) and (
           (not is_num and not is_number_string(input_str[end:]))
           or (is_num and is_digit(input_str[end])))):
        end = end + 1
    return input_str[:end]

def compare_sections(str1:str=None, str2:str=None):
    """
    Compare to string sections.
    Sections should contain either only string data or numerical data.

    :param str1: 1st string to compare, defaults to None
    :type str1: str, optional
    :param str2: 2nd string to compare, defaults to None
    :type str2: str, optional
    :return: String which should come first
    :rtype: str
    """
    # RETURN 0 IF EITHER STRING IS INVALID
    if str1 is None or str2 is None:
        return 0
    # COMPARE SECTIONS
    digit1 = is_number_string(str1)
    digit2 = is_number_string(str2)
    if digit1 and digit2 and len(str1) < 11 and len(str2) < 11:
        # IF BOTH SECTIONS ARE NUMBERS, COMPARE NUMERICALLY
        try:
            val1 = float(str1.replace(",", "."))
            val2 = float(str2.replace(",", "."))
            if val1 < val2:
                return -1
            elif val1 > val2:
                return 1
            else:
                return 0
        except ValueError:
            pass
    return compare_strings(str1, str2)

def compare_alphanum(str1:str=None, str2:str=None):
    """
    Compare two strings alphabetically and numerically.
    Not case sensitive.

    :param str1: 1st string to compare, defaults to None
    :type str1: str, optional
    :param str2: 2nd string to compare, defaults to None
    :type str2: str, optional
    :return: String which should come first
    :rtype: str
    """
    # RETURN 0 IF EITHER STRING IS INVALID
    if str1 is None or str2 is None:
        return 0
    # BREAK INTO SECTIONS AND COMPARE
    result = 0
    end1 = str1
    end2 = str2
    while (result == 0 and (not end1 == "" or not end2 == "")):
        section1 = get_section(end1)
        section2 = get_section(end2)
        end1 = end1[len(section1):]
        end2 = end2[len(section2):]
        result = compare_sections(section1, section2)
    return result
