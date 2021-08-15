#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import deepcopy
from mitosheet.sheet_functions.types.utils import NUMBER_SERIES
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.state import State
from typing import Any, Dict, List, Optional
from mitosheet.errors import (
    make_column_exists_error,
    make_no_sheet_error
)

class AddColumnStepPerformer(StepPerformer):
    """""
    A add_column step, which allows you to add a column to 
    a dataframe. 
    """

    @classmethod
    def step_version(cls) -> int:
        return 2

    @classmethod
    def step_type(cls) -> str:
        return 'add_column'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Added a Column'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'add_column_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_header: str,
        column_header_index: int,
        **params
    ) -> State:
            
        # if the sheet doesn't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index):
            raise make_no_sheet_error(sheet_index)

        if column_header in prev_state.column_metatype[sheet_index]:
            raise make_column_exists_error(column_header)

        # We add a new step with the added column
        post_state = deepcopy(prev_state)

        # If the column_header_index is out of range, then make the new column the last column
        if column_header_index < 0 or len(prev_state.dfs[sheet_index].columns) <= column_header_index:
            column_header_index = len(prev_state.dfs[sheet_index].columns)

        # Update the state variables
        post_state.column_metatype[sheet_index][column_header] = 'formula'
        post_state.column_type[sheet_index][column_header] = NUMBER_SERIES
        post_state.column_spreadsheet_code[sheet_index][column_header] = '=0'
        post_state.column_python_code[sheet_index][column_header] = f'df[\'{column_header}\'] = 0'
        post_state.column_evaluation_graph[sheet_index][column_header] = set()
        post_state.column_filters[sheet_index][column_header] = {'operator': 'And', 'filters': []}
            
        # Update the dataframe
        post_state.dfs[sheet_index].insert(column_header_index, column_header, 0)
        
        return post_state, {
            'column_header_index': column_header_index
        }

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_header: str,
        column_header_index: int
    ) -> List[str]:

        return [
            f'{post_state.df_names[sheet_index]}.insert({execution_data["column_header_index"]}, \'{column_header}\', 0)'
        ]

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_header: str,
        column_header_index: int,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Added column {column_header} to {df_name}'
        return f'Added column {column_header}' 