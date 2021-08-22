#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import copy
from typing import Any, Dict, List, Optional
from mitosheet.state import State
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.utils import make_valid_header
from mitosheet.step_performers.dataframe_steps.dataframe_duplicate import get_first_unused_name

class DataframeRenameStepPerformer(StepPerformer):
    """"
    A rename dataframe step changes the name of a specific dataframe
    at a specific index.
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'dataframe_rename'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Renamed a Dataframe'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'dataframe_rename_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        sheet_index = params['sheet_index']
        old_dataframe_name = prev_state.df_names[sheet_index]
        params['old_dataframe_name'] = old_dataframe_name
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        old_dataframe_name: str,
        new_dataframe_name: str,
        **params
    ) -> State:
        # Bail early, if there is no change
        if old_dataframe_name == new_dataframe_name:
            return

        # Create a new step and save the parameters
        post_state = copy(prev_state)

        post_state.df_names[sheet_index] = get_valid_dataframe_name(post_state.df_names, new_dataframe_name)

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        old_dataframe_name: str,
        new_dataframe_name: str
    ) -> List[str]:
        if old_dataframe_name == new_dataframe_name:
            return []
        return [f'{post_state.df_names[sheet_index]} = {old_dataframe_name}']

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        old_dataframe_name: str,
        new_dataframe_name: str,
        df_names=None,
        **params
    ) -> str:
        return f'Renamed {old_dataframe_name} to {new_dataframe_name}'


def get_valid_python_variable_name(suggested_dataframe_name):
    """
    Turns the suggested dataframe name into a valid Python identifier.
    """
    # See: https://www.w3schools.com/python/ref_string_isidentifier.asp
    if suggested_dataframe_name.isidentifier():
        return suggested_dataframe_name

    # First, we try and just fill in the non valid characters (like a column header)
    valid_header_version = make_valid_header(suggested_dataframe_name)
    if valid_header_version.isidentifier():
        return valid_header_version

    # Finially prefix with df, so that it doesn't start with a number (as vars cannot)
    return f'df_{valid_header_version}'


def get_valid_dataframe_name(df_names, suggested_dataframe_name):
    """
    Given an attempt at a dataframe name, makes sure that is a valid
    dataframe name (e.g. it is a valid Python identifier, and it is
    not a duplicate).
    """
    valid_identifier = get_valid_python_variable_name(suggested_dataframe_name)
    return get_first_unused_name(df_names, valid_identifier)