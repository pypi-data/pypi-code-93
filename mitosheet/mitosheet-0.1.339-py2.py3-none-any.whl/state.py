#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import deepcopy
from typing import List, OrderedDict
import pandas as pd

from mitosheet.sheet_functions.types.utils import get_mito_type

# Constants for where the dataframe in the state came from
DATAFRAME_SOURCE_PASSED = 'passed' # passed in mitosheet.sheet
DATAFRAME_SOURCE_IMPORTED = 'imported' # imported through a simple import
DATAFRAME_SOURCE_PIVOTED = 'pivoted' # created through a pivot
DATAFRAME_SOURCE_MERGED = 'merged' # created through a merge
DATAFRAME_SOURCE_DUPLICATED = 'duplicated' # created through a sheet duplication


class State():
    """
    State is a container that stores the current state of a Mito analysis,
    where each step that is applied takes a state as input and creates a
    new state as output. 

    It stores the obvious things, like the dataframes and their names, but 
    also other helper pieces of state like: the column formulas, the filters,
    etc.
    """

    def __init__(self, 
            dfs: List[pd.DataFrame], 
            df_names: List[str]=None,
            df_sources: List[str]=None,
            column_metatype=None,
            column_type=None,
            column_spreadsheet_code=None,
            column_python_code=None,
            column_evaluation_graph=None,
            column_filters=None
        ):

        # The dataframes that are in the state
        self.dfs = dfs

        # The df_names are composed of two parts:
        # 1. The names of the variables passed into the mitosheet.sheet call (which don't change over time).
        # 2. The names of the dataframes that were created during the analysis (e.g. by a merge).
        # Until we get them from the frontend as an update_event, we default them to df1, df2, ...
        self.df_names = df_names if df_names is not None else [f'df{i + 1}' for i in range(len(dfs))] 

        # The df sources are where the actual dataframes come from, e.g.
        # how the dataframe was created. If not df sources passed, then this is in the
        # initialize state, and so these dataframes were passed to the mitosheet
        # call
        self.df_sources = df_sources if df_sources is not None else [DATAFRAME_SOURCE_PASSED for _ in dfs]

        # The column_metatype is if it stores formulas or values
        self.column_metatype = column_metatype if column_metatype is not None else [{key: 'value' for key in df.keys()} for df in dfs]

        # The column_type is the type of the series in this column 
        self.column_type = column_type if column_type is not None else [{key: get_mito_type(df[key]) for key in df.keys()} for df in dfs]

        # We make column_spreadsheet_code an ordered dictonary to preserve the order the formulas
        # are inserted, which in turn makes sure when we save + rerun an analysis, it's recreated
        # in the correct order (and thus the column order is preserved).
        self.column_spreadsheet_code = column_spreadsheet_code if column_spreadsheet_code is not None else [OrderedDict({key: '' for key in df.keys()}) for df in dfs]
        self.column_python_code = column_python_code if column_python_code is not None else [{key: '' for key in df.keys()} for df in dfs]
        self.column_evaluation_graph = column_evaluation_graph if column_evaluation_graph is not None else [{key: set() for key in df.keys()} for df in dfs]
        self.column_filters = column_filters if column_filters is not None else [{key: {'operator': 'And', 'filters': []} for key in df.keys()} for df in dfs]

    
    def __copy__(self):
        """
        If you copy a state using the copy() function, this Python
        function is called, and returns a shallow copy of the state
        """
        return State(
            [df.copy(deep=False) for df in self.dfs],
            df_names=deepcopy(self.df_names),
            df_sources=deepcopy(self.df_sources),
            column_metatype=deepcopy(self.column_metatype),
            column_type=deepcopy(self.column_type),
            column_spreadsheet_code=deepcopy(self.column_spreadsheet_code),
            column_python_code=deepcopy(self.column_python_code),
            column_evaluation_graph=deepcopy(self.column_evaluation_graph),
            column_filters=deepcopy(self.column_filters)
        )


    def __deepcopy__(self, memo):
        """
        If you copy a state using the deepcopy() function, this Python
        function is called, and returns a deep copy of the state
        """
        return State(
            [df.copy(deep=True) for df in self.dfs],
            df_names=deepcopy(self.df_names),
            df_sources=deepcopy(self.df_sources),
            column_metatype=deepcopy(self.column_metatype),
            column_type=deepcopy(self.column_type),
            column_spreadsheet_code=deepcopy(self.column_spreadsheet_code),
            column_python_code=deepcopy(self.column_python_code),
            column_evaluation_graph=deepcopy(self.column_evaluation_graph),
            column_filters=deepcopy(self.column_filters)
        )

    def add_df_to_state(
            self, 
            new_df: pd.DataFrame, 
            df_source: str, 
            sheet_index=None,
            df_name=None
        ):
        """
        Helper function for adding a new dataframe to this state,
        and keeping all the other variables in sync.

        If sheet_index is defined, then will replace the dataframe
        that is currently at the index. Otherwise, if sheet_index is
        not defined, then will append the df to the end of the state
        """
        if sheet_index is None:
            # Update dfs by appending new df
            self.dfs.append(new_df)
            # Also update the dataframe name
            if df_name is None:
                self.df_names.append(f'df{len(self.df_names) + 1}')
            else:
                self.df_names.append(df_name)

            # Save the source of this dataframe
            self.df_sources.append(df_source)
            
            # Update all the variables that depend on column_headers
            column_headers = new_df.keys()
            self.column_metatype.append({column_header: 'value' for column_header in column_headers})
            self.column_type.append({column_header: get_mito_type(new_df[column_header]) for column_header in column_headers})
            self.column_spreadsheet_code.append({column_header: '' for column_header in column_headers})
            self.column_python_code.append({column_header: '' for column_header in column_headers})
            self.column_evaluation_graph.append({column_header: set() for column_header in column_headers})
            self.column_filters.append({column_header: {'operator':'And', 'filters': []} for column_header in column_headers})

            # Return the index of this sheet
            return len(self.dfs) - 1
        else:

            # Update dfs by switching which df is at this index specifically
            self.dfs[sheet_index] = new_df
            # Also update the dataframe name, if it is passed. Otherwise, we don't change it
            if df_name is not None:
                self.df_names[sheet_index] = df_name

            # Save the source of this dataframe, if it is passed. Otherwise, don't change it
            if df_source is not None:
                self.df_sources[sheet_index] = df_source
            
            # Update all the variables that depend on column_headers
            column_headers = new_df.keys()
            self.column_metatype[sheet_index] = {column_header: 'value' for column_header in column_headers}
            self.column_type[sheet_index] = {column_header: get_mito_type(new_df[column_header]) for column_header in column_headers}
            self.column_spreadsheet_code[sheet_index] = {column_header: '' for column_header in column_headers}
            self.column_python_code[sheet_index] = {column_header: '' for column_header in column_headers}
            self.column_evaluation_graph[sheet_index] = {column_header: set() for column_header in column_headers}
            self.column_filters[sheet_index] = {column_header: {'operator':'And', 'filters': []} for column_header in column_headers}

            # Return the index of this sheet
            return sheet_index
    
    def does_sheet_index_exist_within_state(self, sheet_index):
        """
        Returns true iff a sheet_index exists within this state
        """
        return not (sheet_index < 0 or sheet_index >= len(self.dfs))

    