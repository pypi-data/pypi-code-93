#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Utilities to help with type functions
"""

from typing import Tuple, Union
import pandas as pd
import numpy as np

# Because type(1) = int, thus 1 is a 'number' in the Mito type system
MITO_PRIMITIVE_TYPE_MAPPING = {
    'boolean': [bool],
    'timestamp': [pd.Timestamp],
    'timedelta': [pd.Timedelta],
    'number': [int, float],
    'string': [str],
}

BOOLEAN_SERIES = 'boolean_series'
DATETIME_SERIES = 'datetime_series'
TIMEDELTA_SERIES = 'timedelta_series'
NUMBER_SERIES = 'number_series'
STRING_SERIES = 'string_series'

# A series of helper functions that help you figure
# out which dtype we're dealing with. NOTE: since some
# of these types can be different varieties (e.g. int can be int64, uint64)
# we try to check for them with simple expressions

def is_bool_dtype(dtype):
    return 'bool' == dtype

def is_int_dtype(dtype):
    return 'int' in dtype

def is_float_dtype(dtype):
    return 'float' in dtype

def is_string_dtype(dtype):
    return dtype == 'object' or dtype == 'str' or dtype == 'string'

def is_datetime_dtype(dtype):
    # NOTE: this should handle all different datetime columns, no matter
    # the timezone, as it checks for string inclusion
    return 'datetime' in dtype

def is_timedelta_dtype(dtype):
    return 'timedelta' in dtype

def get_float_columns(df: pd.DataFrame):
    """
    Returns all the float column_headers in the
    passed dataframe
    """
    float_columns = []
    for column_header in df.columns:
        if is_float_dtype(str(df[column_header].dtype)):
            float_columns.append(column_header)
    return float_columns

def get_datetime_columns(df: pd.DataFrame):
    """
    Returns all the datetime column_headers in the
    passed dataframe
    """
    datetime_columns = []
    for column_header in df.columns:
        if is_datetime_dtype(str(df[column_header].dtype)):
            datetime_columns.append(column_header)
    return datetime_columns

def get_timedelta_columns(df: pd.DataFrame):
    """
    Returns all the timedelta column_headers in the
    passed dataframe
    """
    timedelta_columns = []
    for column_header in df.columns:
        if is_timedelta_dtype(str(df[column_header].dtype)):
            timedelta_columns.append(column_header)
    return timedelta_columns

def get_mito_type(obj):

    if isinstance(obj, pd.Series):
        dtype = str(obj.dtype)
        if is_bool_dtype(dtype):
            return BOOLEAN_SERIES
        elif is_int_dtype(dtype) or is_float_dtype(dtype):
            return NUMBER_SERIES
        elif is_string_dtype(dtype):
            return STRING_SERIES
        elif is_datetime_dtype(dtype):
            return DATETIME_SERIES
        elif is_timedelta_dtype(dtype):
            return TIMEDELTA_SERIES
        else:
            # We default to string, when not sure what else
            return STRING_SERIES

    elif isinstance(obj, pd.Timestamp):
        return 'timestamp'
    elif isinstance(obj, pd.Timedelta):
        return 'timedelta'
    else:
        obj_type = type(obj)

        for key, value in MITO_PRIMITIVE_TYPE_MAPPING.items():
            if obj_type in value:
                return key

    return None


def get_nan_indexes(*argv): 
    """
    Given the list of arguments to a function, as *argv, 
    returns a list of row indexes that is True iff one of the series 
    params is NaN at that index. Otherwise the index is False

    This function is called by the filter_nan decorator 
    """

    # we find the max length of the args because we are unsure ahead of time which arg 
    # is a series. we need the max_length to construct the boolean index array
    max_length = -1
    for arg in argv:
        # check the type to make sure an error is not thrown for calling len() on an int
        if isinstance(arg, pd.Series) and len(arg) > max_length:
            max_length = len(arg)

    # if there are no series, then:
    #   1. there are no NaN values
    #   2. all of the args are a length of 1
    if max_length == -1:
        return pd.Series([False], dtype='bool')

    nan_indexes = pd.Series([False for i in range(max_length)], dtype='bool')

    # for each row, check for NaN values in the function
    for arg in argv:
        if isinstance(arg, pd.Series): 
            nan_indexes = nan_indexes | pd.isna(arg)

    return nan_indexes

def put_nan_indexes_back(series, nan_indexes):
    """
    This functions takes a series and a boolean index list that is True 
    if the index in the series should be NaN and false if it should
    be left alone. 

    Returns the series with the NaN values put in

    This function is called by the as_types decorator 
    """
    original_length = len(nan_indexes)
    final_series = []
    real_index = 0
    non_nan_index = 0

    while real_index < original_length:
        if nan_indexes[real_index]:
            final_series.append(np.NaN)
        else:
            final_series.append(series[non_nan_index])
            non_nan_index += 1
        real_index +=1

    final_series = pd.Series(final_series)
    return final_series

def get_datetime_format(string_series):
    """
    Given a series of datetime strings, detects if the format is MM-DD-YYYY,
    which is the most common format that pandas does not default to.

    In the future, we can extend this to detect other formats. Returns None
    if infer_datetime_format is good enough!
    """
    try:
        # If we can convert all non null inputs, then we assume that pandas
        # is guessing the input correctly
        non_null_inputs = string_series[~string_series.isna()]
        converted = pd.to_datetime(non_null_inputs, errors='coerce', infer_datetime_format=True)
        if converted.isna().sum() > 0:
            raise Exception("Non full conversion")
        return None
    except:
        # Otherwise, we manually figure out the format.
        sample_string_datetime = string_series[string_series.first_valid_index()]
        if "/" in sample_string_datetime: 
            return '%m/%d/%Y'
        else:
            return '%m-%d-%Y'