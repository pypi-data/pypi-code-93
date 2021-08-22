#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
This preprocessor reads in any arguments that are
strings, treats them as file paths, and attempts
to read the in a dataframes.
"""
from mitosheet.step_performers.import_steps.simple_import import get_dataframe_names
from mitosheet.errors import get_recent_traceback_as_list
import pandas as pd
from mitosheet.mito_analytics import log

def get_string_args(args):
    return [arg for arg in args if isinstance(arg, str)]

def execute_preprocess_read_file_paths(args):

    df_args = []
    for arg in args:
        if isinstance(arg, pd.DataFrame):
            df_args.append(arg)
        elif isinstance(arg, str):
            # If it is a string, we try and read it in as a dataframe
            try:
                df_args.append(
                    pd.read_csv(arg)
                )
            except:
                # If this pd.read_csv fails, then we report this error to the user
                # as a failed mitosheet call
                error_message = f'Invalid argument passed to sheet: {arg}. This path could not be read with a pd.read_csv call. Please pass in the parsed dataframe directly.'
                log('mitosheet_sheet_call_failed', {'error': error_message, 'error_traceback': get_recent_traceback_as_list()})
                raise ValueError(error_message)
        else:
            error_message = f'Invalid argument passed to sheet: {arg}. Please pass all dataframes or paths to CSV files.'
            log('mitosheet_sheet_call_failed', {'error': error_message})
            raise ValueError(error_message)
            
    return df_args

def transpile_preprocess_read_file_paths(
        steps_manager
    ):
    """
    Transpiles the reading in of passed file paths to dataframe names, 
    with a simple pd.read_csv call.
    """
    code = []

    # First, we get all the string arguments passed to the sheet call
    str_args = get_string_args(steps_manager.original_args)
    
    # Then, we turn these into dataframe names.
    # NOTE: there is potentially a bug if a user passes in a dataframe
    # with the same name as the the result of the return of this function,
    # but we ignore this for now. E.g. mitosheet.sheet('df1.csv', 'df1_csv') 
    # will cause only variable to exist.
    df_names = get_dataframe_names(str_args, [])

    num_strs = 0
    for arg in steps_manager.original_args:
        if isinstance(arg, str):
            df_name = df_names[num_strs]
            num_strs += 1
            # NOTE: we turn this into a raw string with the leading r, so that 
            # Windows \'s aren't read as unicode sequences
            code.append(
                f'{df_name} = pd.read_csv(r\'{arg}\')'
            )

    if len(code) > 0:
        code.insert(0, '# Read in filepaths as dataframes')
            
    return code


PREPROCESS_READ_FILE_PATH = {
    'execute': execute_preprocess_read_file_paths,
    'transpile': transpile_preprocess_read_file_paths
}