#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
This preprocessing step is responsible for making a copy of all of the
passed arguments, so that dataframes aren't modified incorrectly.
"""
import pandas as pd
from copy import deepcopy

from mitosheet.mito_analytics import log

def execute_copy(args):
    new_args = []
    for arg in args:
        if isinstance(arg, pd.DataFrame):
            # Do a pandas copy if it's a dataframe
            arg_copy = arg.copy(deep=True)
        else:
            # Simple deepcopy if it's a string
            arg_copy = deepcopy(arg)
        new_args.append(arg_copy)
    return new_args




def transpile_copy(
        steps_manager
    ):
    """
    This always returns nothing; we are just making copies
    """
    return []

PREPROCESS_COPY = {
    'execute': execute_copy,
    'transpile': transpile_copy
}