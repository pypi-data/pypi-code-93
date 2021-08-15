#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import deepcopy
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.state import State
from typing import Any, Dict, List, Optional
from mitosheet.errors import (
    make_no_sheet_error,
    make_no_column_error,
)

def get_valid_index(dfs, sheet_index, new_column_index):
    # make sure new_column_index is valid
    if new_column_index < 0:
        new_column_index = 0

    if new_column_index >= len(dfs[sheet_index].columns):
        new_column_index = len(dfs[sheet_index].columns) - 1

    return new_column_index


class ReorderColumnStepPerformer(StepPerformer):
    """""
    A reorder_column step, which allows you to move 
    a column to a different location in the df.
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'reorder_column'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Reordered Columns'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'reorder_column_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_header: str,
        new_column_index: int,
        **params
    ) -> State:
        # if the sheet doesn't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index):
            raise make_no_sheet_error(sheet_index)

        # We check that the column to be reordered exists
        missing_column = set([column_header]).difference(prev_state.column_metatype[sheet_index].keys())
        if len(missing_column) > 0:
            raise make_no_column_error(missing_column)

        new_column_index = get_valid_index(prev_state.dfs, sheet_index, new_column_index)
            
        # Create a new post state
        post_state = deepcopy(prev_state)

        # Actually execute the column reordering
        post_state.dfs[sheet_index] = _execute_reorder_column(
            prev_state.dfs[sheet_index],
            column_header,
            new_column_index
        )

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_header: str,
        new_column_index: int
    ) -> List[str]:
        new_column_index = get_valid_index(prev_state.dfs, sheet_index, new_column_index)
        df_name = post_state.df_names[sheet_index]

        # get columns in df
        columns_list_line = f'{df_name}_columns = [col for col in {df_name}.columns if col != \'{column_header}\']'

        # insert column into correct location 
        insert_line = f'{df_name}_columns.insert({new_column_index}, \'{column_header}\')'
        
        # Apply reorder line
        apply_reorder_line = f'{df_name} = {df_name}[{df_name}_columns]'

        return [columns_list_line, insert_line, apply_reorder_line]

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_header: str,
        new_column_index: int,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Reordered {column_header} in {df_name}'
        return f'Reordered {column_header}'


def _execute_reorder_column(df, column_header, new_column_index):
    """
    Helper function for reordering a column in the dataframe
    """
    df_columns = [col for col in df.columns if col != column_header]
    df_columns.insert(new_column_index, column_header)
    return df[df_columns]