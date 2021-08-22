#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
This file contains helpful functions and classes for testing operations.
"""

from typing import List
from mitosheet.utils import get_new_id
import pandas as pd
from mitosheet.transpiler.transpile import transpile

from mitosheet.mito_widget import sheet, MitoWidget
import json

class MitoWidgetTestWrapper:
    """
    This class adds some simple wrapper functions onto the MitoWidget 
    to make interacting with it easier for testing purposes.

    It allows you to create just the backend piece of Mito, create columns,
    set formulas, and get values to check the result.
    """

    def __init__(self, mito_widget: MitoWidget):
        self.mito_widget = mito_widget

    @property
    def transpiled_code(self):
        # NOTE: we don't add comments to this testing functionality, so that 
        # we don't have to change tests if we update comments
        return transpile(self.mito_widget.steps_manager, add_comments=False)['code']

    def add_column(self, sheet_index: int, column_header: str, column_header_index=-1):
        """
        Adds a column.
        """

        self.mito_widget.receive_message(self.mito_widget, {
            'event': 'edit_event',
            'id': get_new_id(),
            'type': 'add_column_edit',
            'step_id': get_new_id(),
            'params': {
                'sheet_index': sheet_index,
                'column_header': column_header,
                'column_header_index': column_header_index
            }
        })
    
    def set_formula(
            self, 
            formula: str, 
            sheet_index: int,
            column_header: str, 
            add_column=False,
        ):
        """
        Sets the given column to have formula, and optionally
        adds the column if it does not already exist.
        """
        if add_column:
            self.add_column(sheet_index, column_header)

        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'set_column_formula_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'column_header': column_header,
                    'new_formula': formula,
                }
            }
        )

    def merge_sheets(
            self, 
            how,
            sheet_index_one, 
            merge_key_one, 
            selected_columns_one,
            sheet_index_two, 
            merge_key_two,
            selected_columns_two
        ):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'merge_edit',
                'step_id': get_new_id(),
                'params': {
                    'how': how,
                    'sheet_index_one': sheet_index_one,
                    'merge_key_one': merge_key_one,
                    'selected_columns_one': selected_columns_one,
                    'sheet_index_two': sheet_index_two,
                    'merge_key_two': merge_key_two,
                    'selected_columns_two': selected_columns_two
                }
            }
        )

    def pivot_sheet(
            self, 
            sheet_index, 
            pivot_rows,
            pivot_columns,
            values,
            destination_sheet_index=None,
            step_id=None
        ):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'pivot_edit',
                'step_id': get_new_id() if step_id is None else step_id,
                'params': {
                    'sheet_index': sheet_index,
                    'pivot_rows': pivot_rows,
                    'pivot_columns': pivot_columns,
                    'values': values,
                    'destination_sheet_index': destination_sheet_index
                }
            }
        )

    def filter(
            self, 
            sheet_index, 
            column,
            operator,
            type_,
            condition, 
            value
        ):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'filter_column_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'column_header': column,
                    'operator': operator,
                    'filters': [{
                        'type': type_,
                        'condition': condition,
                        'value': value
                    }]
                }
            }
        )
    
    def filters(
            self, 
            sheet_index, 
            column,
            operator,
            filters
        ):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'filter_column_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'column_header': column,
                    'operator': operator,
                    'filters': filters
                }
            }
        )
    
    def sort(
            self, 
            sheet_index, 
            column,
            sort_direction
        ):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'sort_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'column_header': column,
                    'sort_direction': sort_direction
                }
            }
        )

    def reorder_column(
            self, 
            sheet_index, 
            column_header, 
            new_column_index
        ):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'reorder_column_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'column_header': column_header,
                    'new_column_index': new_column_index
                }
            }
        )

    def rename_column(self, sheet_index: int, old_column_header: str, new_column_header):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'rename_column_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'old_column_header': old_column_header,
                    'new_column_header': new_column_header
                }
            }
        )

    def delete_column(self, sheet_index: int, column_header: str):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'delete_column_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'column_header': column_header
                }
            }
        )

    def change_column_dtype(self, sheet_index: int, column_header: str, new_dtype: str):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'change_column_dtype_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'column_header': column_header,
                    'new_dtype': new_dtype
                }
            }
        )

    def simple_import(self, file_names: List[str]):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'simple_import_edit',
                'step_id': get_new_id(),
                'params': {
                    'file_names': file_names
                }
            }
        )

    
    def undo(self):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'undo'
            }
        )
    
    def redo(self):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'redo'
            }
        )

    def clear(self):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'clear'
            }
        )
    
    def save_analysis(self, analysis_name):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'save_analysis_update',
                'analysis_name': analysis_name
            }
        )


    def rename_analysis(self, old_analysis_name, new_analysis_name):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'rename_analysis_update',
                'old_analysis_name': old_analysis_name,
                'new_analysis_name': new_analysis_name
            }
        )

    
    def delete_analysis(self, analysis_name):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'delete_analysis_update',
                'analysis_name': analysis_name
            }
        )

    def delete_dataframe(self, sheet_index):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'dataframe_delete_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index
                }
            }
        )

    def duplicate_dataframe(self, sheet_index):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'dataframe_duplicate_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                }
            }
        )

    def rename_dataframe(self, sheet_index, new_dataframe_name):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'edit_event',
                'id': get_new_id(),
                'type': 'dataframe_rename_edit',
                'step_id': get_new_id(),
                'params': {
                    'sheet_index': sheet_index,
                    'new_dataframe_name': new_dataframe_name
                }
            }
        )

    def replay_analysis(self, analysis_name, import_summaries=None, clear_existing_analysis=False):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'replay_analysis_update',
                'analysis_name': analysis_name,
                'import_summaries': import_summaries,
                'clear_existing_analysis': clear_existing_analysis
            }
        )

    def checkout_step_by_idx(self, index):
        self.mito_widget.receive_message(
            self.mito_widget,
            {
                'event': 'update_event',
                'id': get_new_id(),
                'type': 'checkout_step_by_idx_update',
                'step_idx': index,
            }
        )

    def get_formula(self, sheet_index: int, column_header: str):
        """
        Gets the formula for a given column. Returns an empty
        string if nothing exists.
        """
        if column_header not in self.mito_widget.column_spreadsheet_code[sheet_index]:
            return ''
        return self.mito_widget.column_spreadsheet_code[sheet_index][column_header]

    def get_value(self, sheet_index: int, column_header: str, row: int):
        """
        Returns a value in a given dataframe at the a given
        index in a column. NOTE: the row is 1 indexed!

        Errors if the value does not exist
        """
        return self.mito_widget.steps_manager.curr_step.dfs[sheet_index].at[row - 1, column_header]

    def get_column(self, sheet_index: int, column_header: str, as_list: bool):
        """
        Returns a series object of the given column, or a list if
        as_list is True. 

        Errors if the column does not exist. 
        """
        if as_list:
            return self.mito_widget.steps_manager.dfs[sheet_index][column_header].tolist()
        return self.mito_widget.steps_manager.dfs[sheet_index][column_header]

def create_mito_wrapper(sheet_one_A_data, sheet_two_A_data=None) -> MitoWidgetTestWrapper:
    """
    Returns a MitoWidgetTestWrapper instance wrapped around a MitoWidget
    that contains just a column A, containing sheet_one_A_data.
    
    If sheet_two_A_data is defined, then also creates a second dataframe
    with column A defined as this as well.
    """
    dfs = [pd.DataFrame(data={'A': sheet_one_A_data})]

    if sheet_two_A_data is not None:
        dfs.append(pd.DataFrame(data={'A': sheet_two_A_data}))

    mito_widget = sheet(*dfs)
    return MitoWidgetTestWrapper(mito_widget)

def create_mito_wrapper_dfs(*args):
    """
    Creates a MitoWidgetTestWrapper with a mito instance with the given
    data frames.
    """
    mito_widget = sheet(*args)
    return MitoWidgetTestWrapper(mito_widget)