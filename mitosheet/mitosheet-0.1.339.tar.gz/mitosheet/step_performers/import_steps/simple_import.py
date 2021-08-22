#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from mitosheet.step_performers.step_performer import StepPerformer
import os
from typing import Any, Dict, List, Optional
import pandas as pd
from copy import copy
import json
import csv

from mitosheet.mito_analytics import log
from mitosheet.errors import make_is_directory_error
from os.path import basename, normpath
from mitosheet.utils import get_header_renames, make_valid_header
from mitosheet.state import DATAFRAME_SOURCE_IMPORTED, State


class SimpleImportStepPerformer(StepPerformer):
    """
    A simple import, which allows you to import dataframes 
    with the given file_names, while detecting the correct
    way to import them.
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'simple_import'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Imported CSV Files'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'simple_import_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        file_names: List[str],
        **params
    ) -> State:
        # If any of the files are directories, we throw an error to let
        # the user know
        for file_name in file_names:
            if os.path.isdir(file_name):
                raise make_is_directory_error(file_name)

        # Create a new step
        post_state = copy(prev_state)

        column_header_renames = dict()
        file_delimeters = dict()
        for file_name, df_name in zip(file_names, get_dataframe_names(file_names, post_state.df_names)):

            delimeter = guess_delimeter(file_name)
            file_delimeters[df_name] = delimeter

            if delimeter != ',':
                log('used_non_standard_delimeter', {'delimeter': delimeter})

            df = pd.read_csv(file_name, sep=delimeter)
            renames = get_header_renames(df.keys())
            if len(renames) > 0:
                # Save that we did these renames
                column_header_renames[df_name] = renames
                # Actually perform any renames we need to
                df.rename(columns=renames, inplace=True)

            post_state.add_df_to_state(df, DATAFRAME_SOURCE_IMPORTED, df_name=df_name)        

        # Save the renames that have occured in the step, for transpilation reasons
        # and also save the seperator that we used for each file
        return post_state, {
            'column_header_renames': column_header_renames,
            'file_delimeters': file_delimeters
        }

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        file_names: List[str]
    ) -> List[str]:
        code = ['import pandas as pd']
        for file_name, df_name in zip(file_names, post_state.df_names[len(post_state.df_names) - len(file_names):]):

            delimeter = execution_data['file_delimeters'][df_name]

            if delimeter == ',':
                # We don't add the delimeter if it's the default comma
                # NOTE: we add a r in front of the string so that it is a raw string
                # and file slashes are not interpreted as a unicode sequence
                code.append(
                    f'{df_name} = pd.read_csv(r\'{file_name}\')'
                )
            else:
                # If there is a delimeter for this file, we use it
                # NOTE: we add a r in front of the string so that it is a raw string
                # and file slashes are not interpreted as a unicode sequence
                code.append(
                    f'{df_name} = pd.read_csv(r\'{file_name}\', sep=\'{delimeter}\')'
                )
            # If we had to rename columns, mark that as well
            if df_name in execution_data['column_header_renames']:
                renames = execution_data['column_header_renames'][df_name]
                code.append(
                    f'{df_name}.rename(columns={json.dumps(renames)}, inplace=True)'
                )

        return code

    @classmethod
    def describe(
        cls,
        file_names: List[str],
        df_names=None,
        **params
    ) -> str:
        return f'Imported {", ".join(file_names)}'


def guess_delimeter(file_name: str):
    """
    Given a path to a file that is assumed to exist and be a CSV, this
    function guesses the delimeter that is used by that file
    """
    s = csv.Sniffer()
    with open(file_name, 'r') as f:
        return s.sniff(f.readline()).delimiter


def file_name_to_df_name(file_name: str):
    # First, we strip off any path beyond the final filename
    file_name = basename(normpath(file_name))

    # We abuse the fact that all valid mito headers are almost valid variable names
    # If they start w/ numbers, we add letters
    possible_var_name = make_valid_header(file_name)
    if len(possible_var_name) == 0 or possible_var_name[0].isnumeric():
        return 'df_' + possible_var_name
    return possible_var_name


def get_dataframe_names(file_names, existing_df_names):
    """
    Helper function for taking a list of file names and turning them into valid
    names for dataframes.

    NOTE:
    1. If there are duplicates, appends onto the end of them to deduplicate.
    2. Avoids overwriting existing df names.
    """
    new_names_inital = [file_name_to_df_name(file_name) for file_name in file_names]

    final_names = []

    # Keep appending names till we get one that doesn't overlap
    for name in new_names_inital:
        curr_name = name
        count = 0
        while curr_name in final_names or curr_name in existing_df_names:
            curr_name = f'{name}_{count}'
            count += 1
        
        final_names.append(curr_name)
    
    return final_names