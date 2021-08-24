#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Contains all functions that can be used in a sheet that operate on
datetime objects.

All functions describe their behavior with a function documentation object
in the function docstring. Function documentation objects are described
in more detail in docs/README.md.

NOTE: This file is alphabetical order!
"""
from mitosheet.sheet_functions.types.utils import DATETIME_SERIES
import pandas as pd

from mitosheet.sheet_functions.types.decorators import convert_arg_to_series_type, filter_nans, handle_sheet_function_errors


@handle_sheet_function_errors
@filter_nans
@convert_arg_to_series_type(
    0,
    DATETIME_SERIES,
    'error',
    'error'
)
def DATEVALUE(datetime_series) -> pd.Series:
    """
    {
        "function": "DATEVALUE",
        "description": "Converts a given string to a date series.",
        "examples": [
            "DATEVALUE(A)",
            "DATEVALUE('2012-12-22')"
        ],
        "syntax": "DATEVALUE(date_string)",
        "syntax_elements": [{
                "element": "date_string",
                "description": "The date string to turn into a date object."
            }
        ]
    }
    """
    return datetime_series


@handle_sheet_function_errors
@filter_nans
@convert_arg_to_series_type(
    0,
    DATETIME_SERIES,
    'error',
    'error'
)
def DAY(datetime_series) -> pd.Series:
    """
    {
        "function": "DAY",
        "description": "Returns the day of the month that a specific date falls on, as a number.",
        "examples": [
            "DAY(A)",
            "DAY('2012-12-22')"
        ],
        "syntax": "DAY(date)",
        "syntax_elements": [{
                "element": "date",
                "description": "The date or date series to get the day of."
            }
        ]
    }
    """
    return datetime_series.dt.day


@handle_sheet_function_errors
@filter_nans
@convert_arg_to_series_type(
    0,
    DATETIME_SERIES,
    'error',
    'error'
)
def MONTH(datetime_series) -> pd.Series:
    """
    {
        "function": "MONTH",
        "description": "Returns the month that a specific date falls in, as a number.",
        "examples": [
            "MONTH(A)",
            "MONTH('2012-12-22')"
        ],
        "syntax": "MONTH(date)",
        "syntax_elements": [{
                "element": "date",
                "description": "The date or date series to get the month of."
            }
        ]
    }
    """
    return datetime_series.dt.month


@handle_sheet_function_errors
@filter_nans
@convert_arg_to_series_type(
    0,
    DATETIME_SERIES,
    'error',
    'error'
)
def WEEKDAY(datetime_series) -> pd.Series:
    """
    {
        "function": "WEEKDAY",
        "description": "Returns the day of the week that a specific date falls on. 1-7 corresponds to Monday-Sunday.",
        "examples": [
            "WEEKDAY(A)",
            "WEEKDAY('2012-12-22')"
        ],
        "syntax": "WEEKDAY(date)",
        "syntax_elements": [{
                "element": "date",
                "description": "The date or date series to get the weekday of."
            }
        ]
    }
    """
    return datetime_series.dt.weekday + 1


@handle_sheet_function_errors
@filter_nans
@convert_arg_to_series_type(
    0,
    DATETIME_SERIES,
    'error',
    'error'
)
def YEAR(datetime_series) -> pd.Series:
    """
    {
        "function": "YEAR",
        "description": "Returns the day of the year that a specific date falls in, as a number.",
        "examples": [
            "YEAR(A)",
            "YEAR('2012-12-22')"
        ],
        "syntax": "YEAR(date)",
        "syntax_elements": [{
                "element": "date",
                "description": "The date or date series to get the month of."
            }
        ]
    }
    """
    return datetime_series.dt.year


# TODO: we should see if we can list these automatically!
DATE_FUNCTIONS = {
    'DATEVALUE': DATEVALUE,
    'DAY': DAY,
    'MONTH': MONTH,
    'WEEKDAY': WEEKDAY,
    'YEAR': YEAR,
}