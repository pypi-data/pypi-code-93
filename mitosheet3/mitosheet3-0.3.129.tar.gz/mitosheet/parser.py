#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Exports the evaluate function, which takes a list of edit events
as well as the original dataframe, and returns the current state 
of the sheet as a dataframe
"""
import re
from itertools import chain

from mitosheet.errors import make_invalid_formula_error

def get_string_ranges(formula):
    """
    Returns a list of all the ranges that are strings within a formula.

    Useful for other functions that want to "not change strings."
    """
    if formula is None:
        return None

    # We find the ranges of the formula that are string constants;
    # we do not edit these! Taken from: https://stackoverflow.com/a/63707053/13113837
    string_matches_double_quotes = re.finditer(r'"(?:(?:(?!(?<!\\)").)*)"', formula)
    string_matches_single_quotes = re.finditer(r'\'(?:(?:(?!(?<!\\)\').)*)\'', formula)
    string_ranges = []
    for string_match in chain(string_matches_double_quotes, string_matches_single_quotes):
        string_ranges.append(string_match.span())

    return string_ranges

def match_in_strings(string_ranges, match):
    """
    Returns True iff a given match is within one of the string ranges.
    """
    text: str = match.group()
    start = match.start()
    end = match.end() # this is +1 after the last char of the string

    # We check if it's in any of the string ranges
    for string_range in string_ranges:
        string_start = string_range[0]
        string_end = string_range[1]

        if (string_start <= start and string_end >= end):
            return True

    return False

def safe_contains(formula, substring):
    """
    Returns true if the formula contains substring. However, will not count
    the substring if it is inside of a string.

    NOTE: this assumes the formula is valid!
    """

    # we do not search inside the string literals! 
    string_ranges = get_string_ranges(formula)

    for match in re.finditer(substring, formula):
        if not match_in_strings(string_ranges, match):
            return True

    return False

def safe_contains_function(formula, function):
    """
    Checks if a function is called in a formula.
    """
    formula = formula.upper()
    function = function.upper()

    # we do not search inside the string literals! 
    string_ranges = get_string_ranges(formula)

    for match in re.finditer(function, formula):
        if not match_in_strings(string_ranges, match):
            # Check if this is a function
            text: str = match.group()
            end = match.end() # this is +1 after the last char of the string
            if end < len(formula) and formula[end] == '(':
                return True

    return False


def safe_count_function(formula, substring):
    """
    Counts the number of occurences of the substring in the formula
    not including the string ranges

    NOTE: is case insensitive!
    """
    formula = formula.upper()
    function = substring.upper()

    # we do not search inside the string literals! 
    string_ranges = get_string_ranges(formula)

    count = 0
    for match in re.finditer(function, formula):
        if not match_in_strings(string_ranges, match):
            count += 1
    
    return count


def safe_replace(formula, old_text, new_text):
    """
    Given a raw spreadsheet formula, will replace all instances of old_text
    with new_text. 

    However, will not replace any of these instances _within_ strings
    within the formula itself.

    NOTE: this assumes the formula is valid!

    NOTE: old_text and new_text _must_ be words themselves, which means they are
    made up of A-Z, a-z, 0-9, and _.
    """

    if formula is None:
        return None

    # we do not edit inside the string literals! 
    string_ranges = get_string_ranges(formula)

    def replace(match):
        text: str = match.group()

        if match_in_strings(string_ranges, match):
            return text

        # Return the new text if it's the old text
        if text == old_text:
            return new_text

        return text
    
    # Perform the replacement
    return re.sub('\w+', replace, formula)


def check_common_errors(formula: str):
    """
    Helper function for checking a formula for common errors, for better
    communication with users. 

    If you want to throw a custom, specific error that is common for users 
    that can be detected when parsing a formula, add it here!
    """

    if safe_contains(formula, "<>"):
        raise make_invalid_formula_error(
            formula,
            'Please use != instead of <> to check inequality.'
        )

    # If the user used a lookup formula, point them to merge instead!
    LOOKUP_FORMULAS = ['VLOOKUP', 'HLOOKUP', 'XLOOKUP', 'LOOKUP']
    for lookup_formula in LOOKUP_FORMULAS:
        if safe_contains_function(formula.upper(), lookup_formula):
            raise make_invalid_formula_error(
                formula,
                f'Instead of {lookup_formula}, try using the merge button in the toolbar!'
            )
        
    if safe_count_function(formula, '\(') != safe_count_function(formula, '\)'):
        raise make_invalid_formula_error(
            formula,
            f'Sorry, it looks like your parentheses are uneven. Did you close them correctly?'
        )



def parse_formula(formula, address, throw_errors=True):
    """
    Returns a representation of the formula that is easy to handle.

    Specifically, this function returns the triple:
    (python_code, functions, dependencies).

    python_code : a string of Python code that executes
    this formula.
    functions : a set of a strings (function names) that 
    are called
    dependencies : a set of columns this formula references
    """
    if formula is None:
        return '', set(), set()

    # Check the formula for common errors, before parsing it
    # NOTE: this function throws errors!
    if throw_errors:
        check_common_errors(formula)

    # Chop off the =, if it exists. We also accept formulas
    # that don't have an equals
    if formula.startswith('='):
        formula = formula[1:]

    # we do not edit inside the string literals! 
    string_ranges = get_string_ranges(formula)

    functions = set()
    dependencies = set()
    def replace(match):
        """
        Each word match can be:
            1. A constant.
                - A number. Thus, all characters must be digits
                - A string. Must be surrounded by single or double quotes.
                - A boolean. True or False only.
            2. A function call. 
                - This MUST be followed by a '('
            3. A column_reference
                - Any word that isn't any of the above!
        """
        text: str = match.group()
        start = match.start()
        end = match.end() # this is +1 after the last char of the string

        # We skip this token if it is within a string!
        if match_in_strings(string_ranges, match):
            return text

        # CONSTANTS

        # Number
        if text.isnumeric():
            return text
        # String (check it's in quotes)
        if start - 1 >= 0 and (formula[start - 1] == '\"' or formula[start - 1] == '\'') \
            and end < len(formula) and (formula[end] == '\"' or formula[end] == '\''):
            return text
        # Boolean
        if text == 'True' or text == 'False':
            return text

        # Function
        if end < len(formula) and formula[end] == '(':
            # We turn all used functions into upper case in the translated Python
            # NOTE: this does not effect the original spreadsheet formula, which
            # may remaind lower case. 
            function = text.upper()
            functions.add(function)
            return function

        # Finially, columns
        dependencies.add(text)
        return f'df[\'{text}\']'
    
    # We match all words in formula, and send them through the replace function.
    # See documentation here: https://docs.python.org/3/library/re.html#re.sub
    formula = re.sub('\w+', replace, formula)
    
    # Finially, prepend the address to set the dataframe
    formula = f'df[\'{address}\'] = {formula}'

    return formula, functions, dependencies