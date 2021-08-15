#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Contains utilities used in multiple sheet functions.
"""
import pandas as pd
import numpy as np

def fill_series_to_length(series, length):
    """
    Extends a given series to length, padding it with the last
    defined element in the series. 
    Given all dataframes we use are square, this only occurs when one adds
    1 + df['nums'] (where df['nums'] has more than one row), and then our 
    as_type code converts this to:
    pd.Series(data=[1]) + pd.Series(data=[1, 2]) = pd.Series(data=[1, NaN])
    If we ever are adding non-equal length series, we need to fix this!
    """

    # if the series longer than 1, it must be the correct length because 
    # pandas makes dfs square. therefore, filling the series overwrites NaN's
    if len(series) > 1:
        return series

    return series.append(
        pd.Series(data=([None] * (length - len(series)))), ignore_index=True
    ).ffill()

def fill_series_list_to_max(series_list):
    """
    Extends all series in the series_list to the max_length of any series
    in the list, padding them all with their last defined elements. 
    Useful so we can add two series together, as:
    -----
    pd.Series(data=[1]) + pd.Series(data=[1, 2]) = pd.Series(data=[1, Nan])
    -----
    which isn't really what we want!
    """
    max_length = max([series.size for series in series_list])
    return [fill_series_to_length(series, max_length) for series in series_list]