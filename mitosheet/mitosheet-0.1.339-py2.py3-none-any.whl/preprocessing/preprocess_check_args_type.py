#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
This preprocessing step is responsible for making sure the arguments
passed are of the right type.
"""
import pandas as pd

from mitosheet.mito_analytics import log

def execute_check_args_type(args):
    # We first validate all the parameters as either dataframes or strings
    # but we also allow users to pass None values, which we just ignore (this
    # makes variable number of inputs to the sheet possible).
    
    # NOTE: if passing None values to have them ignored, the user should 
    # be careful to place them at the end of the arguments (so df names)
    # read properly and match up with the correct variables
    for arg in args:
        if not isinstance(arg, pd.DataFrame) and not isinstance(arg, str) and not arg is None:
            error_message = f'Invalid argument passed to sheet: {arg}. Please pass all dataframes or paths to CSV files.'
            log('mitosheet_sheet_call_failed', {'error': error_message})
            raise ValueError(error_message)
    
    # We do filter out all the None arguments
    return [arg for arg in args if arg is not None]




def transpile_check_args_type(
        steps_manager
    ):
    """
    This always returns nothing, because there it is just a sanity check
    and does not actually generate any code.
    """
    return []

PREPROCESS_CHECK_ARGS_TYPE = {
    'execute': execute_check_args_type,
    'transpile': transpile_check_args_type
}