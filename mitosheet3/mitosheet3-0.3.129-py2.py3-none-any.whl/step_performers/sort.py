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
    make_invalid_sort_error
)

# CONSTANTS USED IN THE SORT STEP ITSELF
ASCENDING = 'ascending'
DESCENDING = 'descending'

class SortStepPerformer(StepPerformer):
    """
    Allows you to sort a df based on key column, in either
    ascending or descending order.
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'sort'
    
    @classmethod
    def step_display_name(cls) -> str:
        return 'Sorted a Column'

    @classmethod
    def step_event_type(cls) -> str:
        return 'sort_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_header: str,
        sort_direction: str,
        **params
    ):
        """
        Returns the new new post state after sorting the sheet
        at `sheet_index` by the passed `column_header` in the given
        `sort_direction`
        """

        # if the sheet doesn't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index):
            raise make_no_sheet_error(sheet_index)

        # We check that the sorted column exists 
        missing_column = set([column_header]).difference(prev_state.column_metatype[sheet_index].keys())
        if len(missing_column) > 0: 
            raise make_no_column_error(missing_column)

        # We make a new state to modify it
        post_state = deepcopy(prev_state)

        try: 
            new_df = prev_state.dfs[sheet_index].sort_values(by=column_header, ascending=(sort_direction == ASCENDING), na_position='first')
            new_df = new_df.reset_index(drop=True)
            post_state.dfs[sheet_index] = new_df
        except TypeError as e:
            # A NameError occurs when you try to sort a column with incomparable 
            # dtypes (ie: a column with strings and floats)
            print(e)
            # Generate an error informing the user
            raise make_invalid_sort_error(column_header)

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_header: str,
        sort_direction: str
    ) -> List[str]:
        df_name = post_state.df_names[sheet_index]
        return [
            f'{df_name} = {df_name}.sort_values(by=\'{column_header}\', ascending={sort_direction == ASCENDING}, na_position=\'first\')', 
            f'{df_name} = {df_name}.reset_index(drop=True)'
        ]

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_header: str,
        sort_direction: str,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Sorted {column_header} in {df_name} in {sort_direction} order'
        return f'Sorted {column_header} in {sort_direction} order'