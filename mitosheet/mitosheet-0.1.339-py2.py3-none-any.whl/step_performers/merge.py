#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.


from copy import copy
from typing import Any, Dict, List, Optional
from mitosheet.state import DATAFRAME_SOURCE_MERGED, State
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.errors import (
    make_no_sheet_error,
    make_no_column_error,
)


class MergeStepPerformer(StepPerformer):
    """
    Allows you to merge two dataframes together.
    """

    @classmethod
    def step_version(cls) -> int:
        return 2

    @classmethod
    def step_type(cls) -> str:
        return 'merge'
    
    @classmethod
    def step_display_name(cls) -> str:
        return 'Merged Dataframes'

    @classmethod
    def step_event_type(cls) -> str:
        return 'merge_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        how: str,
        sheet_index_one: int,
        merge_key_one: str,
        selected_columns_one: List[str],
        sheet_index_two: int,
        merge_key_two: str,
        selected_columns_two: List[str],
        **params
    ) -> State:
        # if the sheets don't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index_one):
            raise make_no_sheet_error(sheet_index_one)

        if not prev_state.does_sheet_index_exist_within_state(sheet_index_two):
            raise make_no_sheet_error(sheet_index_two)

        # We check that the merge doesn't use any columns that don't exist
        missing_sheet_one_key = {merge_key_one}.difference(prev_state.column_metatype[sheet_index_one].keys())
        if any(missing_sheet_one_key):
            raise make_no_column_error(missing_sheet_one_key)

        missing_sheet_two_key = {merge_key_two}.difference(prev_state.column_metatype[sheet_index_two].keys())
        if any(missing_sheet_two_key):
            raise make_no_column_error(missing_sheet_two_key)

        # We create a shallow copy to make the new post state
        post_state = copy(prev_state)

        new_df = _execute_merge(
            prev_state.dfs,
            prev_state.df_names,
            how,
            sheet_index_one,
            merge_key_one,
            selected_columns_one,
            sheet_index_two,
            merge_key_two,
            selected_columns_two
        )    

        # Add this dataframe to the new post state
        post_state.add_df_to_state(new_df, DATAFRAME_SOURCE_MERGED)

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        how: str,
        sheet_index_one: int,
        merge_key_one: str,
        selected_columns_one: List[str],
        sheet_index_two: int,
        merge_key_two: str,
        selected_columns_two: List[str]
    ) -> List[str]:

        # update df indexes to start at 1
        df_one_name = post_state.df_names[sheet_index_one]
        df_two_name = post_state.df_names[sheet_index_two]
        df_new_name = post_state.df_names[len(post_state.dfs) - 1]

        # Now, we build the merge code 
        merge_code = []
        if how == 'lookup':
            # If the mege is a lookup, then we add the drop duplicates code
            temp_df_name = 'temp_df'
            merge_code.append(f'{temp_df_name} = {df_two_name}.drop_duplicates(subset=\'{merge_key_two}\') # Remove duplicates so lookup merge only returns first match')
            how_to_use = 'left'
        else:
            temp_df_name = df_two_name
            how_to_use = how


        # If we are only taking some columns, write the code to drop the ones we don't need!
        deleted_columns_one = set(post_state.dfs[sheet_index_one].keys()).difference(set(selected_columns_one))
        deleted_columns_two = set(post_state.dfs[sheet_index_two].keys()).difference(set(selected_columns_two))
        if len(deleted_columns_one) > 0:
            merge_code.append(
                f'{df_one_name}_tmp = {df_one_name}.drop({list(deleted_columns_one)}, axis=1)'
            )
        if len(deleted_columns_two) > 0:
            merge_code.append(
                f'{df_two_name}_tmp = {temp_df_name}.drop({list(deleted_columns_two)}, axis=1)'
            )

        # If we drop columns, we merge the new dataframes
        df_one_to_merge = df_one_name if len(deleted_columns_one) == 0 else f'{df_one_name}_tmp'
        df_two_to_merge = temp_df_name if len(deleted_columns_two) == 0 else f'{df_two_name}_tmp'

        # We insist column names are unique in dataframes, so while we default the suffixes to be the dataframe
        # names
        suffix_one = df_one_name
        suffix_two = df_two_name if df_two_name != df_one_name else f'{df_two_name}_2'

        # Finially append the merge
        merge_code.append(
            f'{df_new_name} = {df_one_to_merge}.merge({df_two_to_merge}, left_on=[\'{merge_key_one}\'], right_on=[\'{merge_key_two}\'], how=\'{how_to_use}\', suffixes=[\'_{suffix_one}\', \'_{suffix_two}\'])'
        )

        # And then return it
        return merge_code

    @classmethod
    def describe(
        cls,
        how: str,
        sheet_index_one: int,
        merge_key_one: str,
        selected_columns_one: List[str],
        sheet_index_two: int,
        merge_key_two: str,
        selected_columns_two: List[str],
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_one_name = df_names[sheet_index_one]
            df_two_name = df_names[sheet_index_two]
            return f'Merged {df_one_name} and {df_two_name}'
        return f'Merged dataframes {sheet_index_one} and {sheet_index_two}'

def _execute_merge(
        dfs, 
        df_names,
        how,
        sheet_index_one,
        merge_key_one, 
        selected_columns_one,
        sheet_index_two,
        merge_key_two,
        selected_columns_two
    ):
    """
    Executes a merge on the sheets with the given indexes, merging on the 
    given keys, and only keeping the selection columns from each df.
    """
    if how == 'lookup':
        # We drop duplicates to avoid pairwise duplication on the merge.
        temp_df = dfs[sheet_index_two].drop_duplicates(subset=merge_key_two)
        # We overwrite the how variable to 'left' so it can be used in the merge
        how_to_use = 'left'
    else:
        temp_df = dfs[sheet_index_two]
        how_to_use = how

    # Then we delete all the columns from each we don't wanna keep
    deleted_columns_one = set(dfs[sheet_index_one].keys()).difference(set(selected_columns_one))
    deleted_columns_two = set(dfs[sheet_index_two].keys()).difference(set(selected_columns_two))

    df_one_cleaned = dfs[sheet_index_one].drop(deleted_columns_one, axis=1)
    df_two_cleaned = temp_df.drop(deleted_columns_two, axis=1)

    # Finially, we perform the merge!
    df_one_name = df_names[sheet_index_one]
    df_two_name = df_names[sheet_index_two]
    # We make sure the suffixes aren't the same, as otherwise we might end up with 
    # one df with duplicated column headers
    suffix_one = df_one_name
    suffix_two = df_two_name if df_two_name != df_one_name else f'{df_two_name}_2'

    return df_one_cleaned.merge(df_two_cleaned, left_on=[merge_key_one], right_on=[merge_key_two], how=how_to_use, suffixes=[f'_{suffix_one}', f'_{suffix_two}'])