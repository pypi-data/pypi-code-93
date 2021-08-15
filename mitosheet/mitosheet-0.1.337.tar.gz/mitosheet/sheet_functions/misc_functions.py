#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Contains all functions that don't particularly fit in any other category

All functions describe their behavior with a function documentation object
in the function docstring. Function documentation objects are described
in more detail in docs/README.md.

NOTE: This file is alphabetical order!
"""
from mitosheet.sheet_functions.sheet_function_utils import fill_series_list_to_max, fill_series_to_length
import pandas as pd
import numpy as np
import datetime

from mitosheet.sheet_functions.types.decorators import filter_nans, convert_arg_to_series_type, handle_sheet_function_errors


@handle_sheet_function_errors
@convert_arg_to_series_type(
    0,
    'series',
    'error',
    'error'
)
@convert_arg_to_series_type(
    1,
    'series',
    'error',
    'error'
)
def FILLNAN(series: pd.Series, replacement: pd.Series) -> pd.Series:
    """
    {
        "function": "FILLNAN",
        "description": "Replaces the NaN values in the series with the replacement value.",
        "examples": [
            "FILLNAN(A, 10)",
            "FILLNAN(A, 'replacement')"
        ],
        "syntax": "FILLNAN(series, replacement)",
        "syntax_elements": [{
                "element": "series",
                "description": "The series to replace the NaN values in."
            },
            {
                "element": "replacement",
                "description": "A string, number, or date to replace the NaNs with."
            }
        ]
    }
    """
    # Make sure the replacement series is long enough
    replacement = fill_series_to_length(replacement, len(series))

    return series.fillna(replacement)

@handle_sheet_function_errors
@filter_nans
@convert_arg_to_series_type(
    0,
    'series',
    'error',
    'error'
)
#TODO: Fix up the offset for this function, as it should be forced into a number.
def OFFSET(series: pd.Series, offset) -> pd.Series:
    """
    {
        "function": "OFFSET",
        "description": "Shifts the given series by the given offset. Use a negative offset to reference a previous row, and a offset number to reference a later row.",
        "examples": [
            "OFFSET(Nums, 10)",
            "OFFSET(call_time, -1)"
        ],
        "syntax": "OFFSET(series, offset)",
        "syntax_elements": [{
                "element": "series",
                "description": "The series to shift up or down."
            },
            {
                "element": "offset",
                "description": "An integer amount to shift. Use a negative number to reference a previous row, and a positive number to reference a later row."
            }
        ]
    }
    """
    length = len(series)
    # If the shift is too big, we just return an empty series
    if abs(offset) >= length:
        return pd.Series([np.NaN] * length)
    
    if offset < 0:
        # Otherwise, append the NaNs to the front, and chop at the correct length
        return pd.concat([pd.Series([np.NaN] * (offset * -1)), series], ignore_index=True).head(length)
    else:
        remaining_series = series.tail(length - offset)
        return pd.concat([remaining_series, pd.Series([np.NaN] * offset)], ignore_index=True).head(length)


@handle_sheet_function_errors
@convert_arg_to_series_type(
    0,
    'series',
    'error',
    'error'
)
def TYPE(series: pd.Series) -> pd.Series:
    """
    {
        "function": "TYPE",
        "description": "Returns the type of each element of the passed series. Return values are 'number', 'str', 'bool', 'datetime', 'object', or 'NaN'.",
        "examples": [
            "TYPE(Nums_and_Strings)",
            "IF(TYPE(Account_Numbers) != 'NaN', Account_Numbers, 0)"
        ],
        "syntax": "TYPE(series)",
        "syntax_elements": [{
                "element": "series",
                "description": "The series to get the type of each element of."
            }
        ]
    }
    """

    def get_element_type(element):
        try:
            # Try nan first, this may fail
            if np.isnan(element):
                return 'NaN'
        except:
            pass 

        # Start with bool!
        if isinstance(element, bool):
            return 'bool'
        elif isinstance(element, int):
            return 'number'
        elif isinstance(element, float):
            return 'number'
        elif isinstance(element, str):
            return 'string'
        elif isinstance(element, datetime.datetime):
            return 'datetime'
        elif isinstance(element, pd.Timedelta):
            return 'timedelta'
        return 'object'


    return series.apply(get_element_type).astype('str')




# TODO: we should see if we can list these automatically!
MISC_FUNCTIONS = {
    'FILLNAN': FILLNAN,
    'OFFSET': OFFSET,
    'TYPE': TYPE
}