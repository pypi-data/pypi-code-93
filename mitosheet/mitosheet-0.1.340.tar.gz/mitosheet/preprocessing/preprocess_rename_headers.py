#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
This preprocessing step is responsible for renaming invalid
column headers to headers mito can handle.
"""
import json
import pandas as pd
from mitosheet.utils import get_header_renames, is_valid_header, make_valid_header

def execute_preprocess_rename_headers(args):
    
    # Note, by the time args get here, they should be all dataframes
    # as the CSV paths should be read in by now
    for sheet_index, df in enumerate(args):
        renames = dict()
        for column_header in df.keys():
            if not is_valid_header(column_header):
                valid_header = make_valid_header(column_header)
                renames[column_header] = valid_header
        
        df.rename(columns=renames, inplace=True)

    return args

def transpile_preprocess_rename_headers(
        steps_manager
    ):
    """
    Transpiles an initial column header rename to Python code! 
    May be empty if there is nothing to rename.
    """
    code = []
    for sheet_index, arg in enumerate(steps_manager.original_args):
        if isinstance(arg, pd.DataFrame):
            column_headers = arg.keys()
            renames = get_header_renames(column_headers)
            
            if len(renames) == 0:
                continue

            code.append(
                f'{steps_manager.curr_step.df_names[sheet_index]}.rename(columns={json.dumps(renames)}, inplace=True)'
            )

    if len(code) > 0:
        code.insert(0, '# Rename headers to make them work with Mito')

    return code

PREPROCESS_RENAME_HEADERS = {
    'execute': execute_preprocess_rename_headers,
    'transpile': transpile_preprocess_rename_headers
}