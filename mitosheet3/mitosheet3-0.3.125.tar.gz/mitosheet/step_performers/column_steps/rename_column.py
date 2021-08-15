#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import deepcopy
from mitosheet.step_performers.step_performer import StepPerformer
from typing import Any, Dict, List, Optional
from mitosheet.state import State
from mitosheet.parser import safe_replace
from mitosheet.utils import is_valid_header
from mitosheet.step_performers.column_steps.set_column_formula import _update_column_formula_in_step

from mitosheet.errors import (
    make_invalid_column_headers_error,
    make_column_exists_error, make_no_sheet_error,
)

class RenameColumnStepPerformer(StepPerformer):
    """"
    A rename_column step, which allows you to rename a column
    in a dataframe.
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'rename_column' 

    @classmethod
    def step_display_name(cls) -> str:
        return 'Renamed a Column'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'rename_column_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        old_column_header: str,
        new_column_header: str,
        **params
    ) -> State:
        # if the sheet doesn't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index):
            raise make_no_sheet_error(sheet_index)

        if not is_valid_header(new_column_header):
            raise make_invalid_column_headers_error([new_column_header])

        if new_column_header in prev_state.dfs[sheet_index].keys():
            raise make_column_exists_error(new_column_header)

        # Create a new post state for this step
        post_state = deepcopy(prev_state)

        # Execute the rename
        post_state.dfs[sheet_index].rename(columns={old_column_header: new_column_header}, inplace=True)

        # Then, we update the current step to be valid, namely by deleting the old column (wherever it is)
        # and replacing it with the new column. 
        sheet_column_metatype = post_state.column_metatype[sheet_index]
        sheet_column_metatype[new_column_header] = sheet_column_metatype[old_column_header]

        sheet_column_type = post_state.column_type[sheet_index]
        sheet_column_type[new_column_header] = sheet_column_type[old_column_header]

        sheet_column_spreadsheet_code = post_state.column_spreadsheet_code[sheet_index]
        sheet_column_spreadsheet_code[new_column_header] = sheet_column_spreadsheet_code[old_column_header]

        sheet_column_python_code = post_state.column_python_code[sheet_index]
        sheet_column_python_code[new_column_header] = sheet_column_python_code[old_column_header].replace(
            f'df[\'{old_column_header}\']',
            f'df[\'{new_column_header}\']'
        )
        
        sheet_column_evaluation_graph = post_state.column_evaluation_graph[sheet_index]
        sheet_column_evaluation_graph[new_column_header] = sheet_column_evaluation_graph[old_column_header]

        sheet_column_filters = post_state.column_filters[sheet_index]
        sheet_column_filters[new_column_header] = sheet_column_filters[old_column_header]

        # We also have to go over _all_ the formulas in the sheet that reference this column, and update
        # their references to the new column. 
        for column_header in sheet_column_evaluation_graph[new_column_header]:
            old_formula = sheet_column_spreadsheet_code[column_header]
            new_formula = safe_replace(
                old_formula,
                old_column_header,
                new_column_header
            )

            # NOTE: this does not update the evaluation graph for columns that are descendents
            # of this column, so we do that below.
            _update_column_formula_in_step(post_state, sheet_index, column_header, old_formula, new_formula)

        # We then have to go through and update the evaluation graphs
        # for the columns the renamed column relied on.
        for dependents in sheet_column_evaluation_graph.values():
            if old_column_header in dependents:
                dependents.remove(old_column_header)
                dependents.add(new_column_header)

        # We delete all references to the old_column header
        # NOTE: this has to happen after the above formula setting, so that
        # the dependencies can be updated properly!
        del sheet_column_metatype[old_column_header]
        del sheet_column_type[old_column_header]
        del sheet_column_spreadsheet_code[old_column_header]
        del sheet_column_python_code[old_column_header]
        del sheet_column_evaluation_graph[old_column_header]
        del sheet_column_filters[old_column_header]

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        old_column_header: str,
        new_column_header: str
    ) -> List[str]:
        df_name = post_state.df_names[sheet_index]
        rename_dict = "{\"" + old_column_header + "\": \"" + new_column_header + "\"}"
        return [f'{df_name}.rename(columns={rename_dict}, inplace=True)']

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        old_column_header: str,
        new_column_header: str,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Renamed {old_column_header} to {new_column_header} in {df_name}'
        return f'Renamed {old_column_header} to {new_column_header}'