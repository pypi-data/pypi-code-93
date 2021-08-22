#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import deepcopy
from mitosheet.state import State
from typing import Any, Dict, List, Optional
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.errors import (
    make_no_sheet_error,
    make_no_column_error,
    make_invalid_column_delete_error
)

class DeleteColumnStepPerformer(StepPerformer):
    """"
    A delete_column step, which allows you to delete a column
    from a dataframe.
    """
    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'delete_column'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Deleted a Column'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'delete_column_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_header: str,
        **params
    ) -> State:
        # if the sheet doesn't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index):
            raise make_no_sheet_error(sheet_index)

        # Error if the column does not exist
        if column_header not in prev_state.column_metatype[sheet_index]:
            raise make_no_column_error([column_header])
        
        # Error if there are any columns that currently rely on this column
        if len(prev_state.column_evaluation_graph[sheet_index][column_header]) > 0:
            raise make_invalid_column_delete_error(
                column_header,
                list(prev_state.column_evaluation_graph[sheet_index][column_header])
            )

        # Make a post state, that is a deep copy
        post_state = deepcopy(prev_state)
        
        # Actually drop the column
        df = post_state.dfs[sheet_index]
        df.drop(column_header, axis=1, inplace=True)

        # And then update all the state variables removing this column from the state
        del post_state.column_metatype[sheet_index][column_header]
        del post_state.column_type[sheet_index][column_header]
        del post_state.column_spreadsheet_code[sheet_index][column_header]
        del post_state.column_python_code[sheet_index][column_header]
        del post_state.column_evaluation_graph[sheet_index][column_header]
        # We also have to delete the places in the graph where this node is 
        for dependents in post_state.column_evaluation_graph[sheet_index].values():
            if column_header in dependents:
                dependents.remove(column_header)
        
        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_header: str
    ) -> List[str]:
        df_name = post_state.df_names[sheet_index]
        return [f'{df_name}.drop(\'{column_header}\', axis=1, inplace=True)']

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_header: str,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Deleted column {column_header} from {df_name}'
        return f'Deleted column {column_header}'