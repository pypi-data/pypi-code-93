#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import copy
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.state import DATAFRAME_SOURCE_DUPLICATED, State
from typing import Any, Dict, List, Optional


class DataframeDuplicateStepPerformer(StepPerformer):
    """
    This steps duplicates a dataframe of a given index. 
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'dataframe_duplicate'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Duplicated a Dataframe'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'dataframe_duplicate_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        **params
    ) -> State:
        post_state = copy(prev_state)

        # Execute the step
        df_copy = post_state.dfs[sheet_index].copy(deep=True)
        new_name = get_first_unused_name(post_state.df_names, post_state.df_names[sheet_index] + '_copy')
        post_state.add_df_to_state(df_copy, DATAFRAME_SOURCE_DUPLICATED, df_name=new_name)

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int
    ) -> List[str]:
        old_df_name = post_state.df_names[sheet_index]
        new_df_name = post_state.df_names[len(post_state.dfs) - 1]

        return [f'{new_df_name} = {old_df_name}.copy(deep=True)']

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            old_df_name = df_names[sheet_index]
            new_df_name = df_names[len(df_names) - 1]
            return f'Duplicated {old_df_name} to {new_df_name}'
        return f'Duplicated a df'


def get_first_unused_name(df_names, dataframe_name):
    """
    Appends _1, _2, .. to df name until it finds an unused 
    dataframe name. If no append is necessary, will just return
    """
    if dataframe_name not in df_names:
        return dataframe_name

    for i in range(len(df_names) + 1):
        new_name = f'{dataframe_name}_{i + 1}'
        if new_name not in df_names:
            return new_name