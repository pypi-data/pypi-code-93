#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.


from copy import copy
from mitosheet.state import DATAFRAME_SOURCE_PIVOTED, State
from mitosheet.step_performers.step_performer import StepPerformer
from typing import Any, Dict, List, Optional
from mitosheet.utils import make_valid_header
import pandas as pd
from pandas.core.base import DataError
import pandas as pd

from mitosheet.errors import (
    make_invalid_pivot_error,
    make_no_sheet_error,
    make_no_column_error,
    make_invalid_aggregation_error,
)

# Aggregation types pivot supports
PA_COUNT_UNIQUE = 'count unique'
PIVOT_AGGREGATION_TYPES = [
    # These first few are supported out of the box by 
    # pandas, so we don't need any extra support for them
    'sum',
    'mean',
    'median',
    'min',
    'max', 
    'count', 
    'std',
    PA_COUNT_UNIQUE
]

class PivotStepPerformer(StepPerformer):
    """
    A pivot, which allows you to pivot data from an existing dataframe 
    along some keys, and then aggregate columns with specific functions.
    """

    @classmethod
    def step_version(cls) -> int:
        return 3

    @classmethod
    def step_type(cls) -> str:
        return 'pivot'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Pivoted a Dataframe'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'pivot_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        """
        Saturates the pivot table with just a `created_non_empty_dataframe` key, which
        is useful for logging.

        Furthermore, we filter out any duplicated aggregation keys, as they
        result in errors without adding any data to the pivot.
        """
        # Case 1 - we have at least one row and at least one value
        created_case_1 = len(params['pivot_rows']) > 0 and len(params['values']) > 0
        # Case 2 - we have at least one column and at least one value
        created_case_2 = len(params['pivot_columns']) > 0 and len(params['values']) > 0
        params['created_non_empty_dataframe'] = created_case_1 or created_case_2

        # Filter out any duplicate aggregation functions
        for column_header, aggregation_function_names in params['values'].items():
            seen = set()
            aggregation_function_names = [x for x in aggregation_function_names if not (x in seen or seen.add(x))]
            params['values'][column_header] = aggregation_function_names

        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        pivot_rows: List[str],
        pivot_columns: List[str],
        values: Dict[str, List[str]],
        destination_sheet_index: int=None,
        **params
    ) -> State:

        # if the sheets don't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index):
            raise make_no_sheet_error(sheet_index)

        # We check that the pivot by doesn't use any columns that don't exist
        columns_used = set(pivot_rows).union(set(pivot_columns)).union(set(values.keys()))
        missing_pivot_keys = columns_used.difference(prev_state.column_metatype[sheet_index].keys())
        if len(missing_pivot_keys) > 0:
            raise make_no_column_error(missing_pivot_keys)

        # Create the post state, it can be a shallow copy
        post_state = copy(prev_state)

        try:
            # Actually execute the pivoting
            new_df = _execute_pivot(
                prev_state.dfs[sheet_index], 
                pivot_rows,
                pivot_columns,
                values
            )
            
            destination_sheet_index = post_state.add_df_to_state(
                new_df, 
                DATAFRAME_SOURCE_PIVOTED,
                sheet_index=destination_sheet_index
            )

        except DataError as e:
            # A data-error occurs when you try to aggregate on a column where the function
            # cannot be applied (e.g. 'mean' on a column of strings)
            print(e)
            # Generate an error informing the user
            raise make_invalid_aggregation_error()


        return post_state, {
            'destination_sheet_index': destination_sheet_index
        }

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        pivot_rows: List[str],
        pivot_columns: List[str],
        values: Dict[str, List[str]],
        destination_sheet_index: int=None,
        **params
    ) -> List[str]:
        old_df_name = post_state.df_names[sheet_index]
        if destination_sheet_index is None:
            new_df_name = f'df{len(post_state.dfs)}'
        else:
            # If we're repivoting an existing pivot table, we have
            # to make sure to overwrite the correct pivot table 
            # by using the right name
            new_df_name = post_state.df_names[destination_sheet_index]
        
        # If there are no keys or values to aggregate on we return an empty dataframe. 
        if len(pivot_rows) == 0 and len(pivot_columns) == 0 or len(values) == 0:
            return [f'{new_df_name} = pd.DataFrame(data={{}})']

        transpiled_code = []

        # Drop any columns we don't need, to avoid issues where pandas freaks out
        # and says there is a non-1-dimensional grouper
        transpiled_code.append(f'unused_columns = {old_df_name}.columns.difference(set({pivot_rows}).union(set({pivot_columns})).union(set({set(values.keys())})))')
        transpiled_code.append(f'tmp_df = {old_df_name}.drop(unused_columns, axis=1)')

        # Do the actual pivot
        pivot_table_args = build_args_code(pivot_rows, pivot_columns, values)
        transpiled_code.append(f'pivot_table = tmp_df.pivot_table({NEWLINE_TAB}{pivot_table_args}\n)')

        # Flatten column headers, which we always do because it's hard to tell when we should
        transpiled_code.append(FLATTEN_COMMENT)
        transpiled_code.append(FLATTEN_CODE)

        # Finially, reset the column name, and the indexes!
        transpiled_code.append(RESET_INDEX_COMMENT)
        transpiled_code.append(f'{new_df_name} = pivot_table.rename_axis(None, axis=1).reset_index()')

        return transpiled_code

    @classmethod
    def describe(
        cls,
        sheet_index,
        pivot_rows,
        pivot_columns,
        values,
        destination_sheet_index=None,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            new_df_name = f'df{len(df_names)}'
            old_df_name = df_names[sheet_index]
            return f'Pivoted {old_df_name} into {new_df_name}'
        return f'Pivoted dataframe {sheet_index}'


def values_to_functions(values):
    """
    Helper function for turning the values mapping sent by the frontend to the values
    mapping to functions that can actually be passed to the pandas pivot function
    """
    new_values = dict()

    for column_header, aggregation_function_names in values.items():
        new_values[column_header] = []
        for agg_func_name in aggregation_function_names:
            if agg_func_name not in PIVOT_AGGREGATION_TYPES:
                raise make_invalid_pivot_error()

            if agg_func_name == PA_COUNT_UNIQUE:
                agg_func = pd.Series.nunique
            else:
                agg_func = agg_func_name
                
            new_values[column_header].append(agg_func)
    
    return new_values

def _execute_pivot(
        df: pd.DataFrame, 
        pivot_rows: List[str], 
        pivot_columns: List[str], 
        values
    ):
    """
    Helper function for executing the pivot on a specific dataframe
    and then aggregating the values with the passed values mapping
    """

    # If there are no keys to aggregate on, we return an empty dataframe
    if (len(pivot_rows) == 0 and len(pivot_columns) == 0) or len(values) == 0:
        return pd.DataFrame(data={})

    values_keys = list(values.keys())

    # Built the args, leaving out any unused values
    args = {}

    if len(pivot_rows) > 0:
        args['index'] = pivot_rows

    if len(pivot_columns) > 0:
        args['columns'] = pivot_columns

    if len(values) > 0:
        args['values'] = values_keys
        args['aggfunc'] = values_to_functions(values)


    # Before execution, we make a temp dataframe that does not have the columns 
    # we do not need, as this allows us to avoid a bug in pandas where these extra
    # columns cause a data
    unused_columns = df.columns.difference(set(pivot_rows).union(set(pivot_columns)).union(set(values_keys)))
    df = df.drop(unused_columns, axis=1)

    # Actually perform the pivot
    pivot_table = df.pivot_table(**args) # type: pd.DataFrame

    # Flatten the column headers
    pivot_table.columns = [make_valid_header(col) for col in pivot_table.columns.values]

    # flatten the column headers & reset the indexes
    pivot_table = pivot_table.rename_axis(None, axis=1).reset_index()

    return pivot_table

def values_to_functions_code(values):
    """
    Helper function for turning the values mapping sent by the frontend to the values
    mapping that works in generated code. Namely, needs to replay Count Unique with the
    function pd.Series.nunique.
    """
    string_values = f'{values}'
    # NOTE: this needs to match the values sent from the frontend
    # also note that we overwrite the quotes around Count Unique
    return string_values.replace('\'count unique\'', 'pd.Series.nunique')

# Helpful constants for code formatting
TAB = '    '
NEWLINE_TAB = f'\n{TAB}'

FLATTEN_COMMENT = '# Flatten the column headers'
FLATTEN_CODE = f'pivot_table.columns = [make_valid_header(col) for col in pivot_table.columns.values]'
RESET_INDEX_COMMENT = '# Reset the column name and the indexes'


def build_args_code(
        pivot_rows,
        pivot_columns,
        values
    ):
    """
    Helper function for building an arg string, while leaving
    out empty arguments. 
    """
    values_keys = list(values.keys())

    args = []
    if len(pivot_rows) > 0:
        args.append(f'index={pivot_rows},')

    if len(pivot_columns) > 0:
        args.append(f'columns={pivot_columns},')

    if len(values) > 0:
        args.append(f'values={values_keys},')
        args.append(f'aggfunc={values_to_functions_code(values)}')
        
    return NEWLINE_TAB.join(args)