#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

from copy import copy
from mitosheet.state import State
from typing import Any, Dict, List, Optional
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.mito_analytics import log
from mitosheet.errors import make_invalid_column_type_change_error
from mitosheet.sheet_functions.types.to_number_series import to_number_series
from mitosheet.sheet_functions.types.to_boolean_series import to_boolean_series
from mitosheet.sheet_functions.types.utils import (
    get_datetime_format, get_mito_type, is_bool_dtype, is_float_dtype, is_int_dtype,
    is_string_dtype, is_datetime_dtype, is_timedelta_dtype
) 
import pandas as pd

 
class ChangeColumnDtypeStepPerformer(StepPerformer):
    """"
    A step that allows changing the dtype of a column to a different
    dtype.

    Currently, supports: 'bool', 'int', 'float', 'str', 'datetime', 'timedelta'
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'change_column_dtype'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Change column dtype'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'change_column_dtype_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        params['old_dtype'] = str(prev_state.dfs[params['sheet_index']][params['column_header']].dtype)
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_header: str,
        old_dtype: str,
        new_dtype: str,
        **params
    ) -> State:
        # Create the post state
        post_state = copy(prev_state)
        
        column: pd.Series = prev_state.dfs[sheet_index][column_header]
        new_column = column
        
        # How we handle the type conversion depends on what type it is
        try:
            if is_bool_dtype(old_dtype):
                if is_bool_dtype(new_dtype):
                    pass
                elif is_int_dtype(new_dtype):
                    new_column = new_column.astype('int')
                elif is_float_dtype(new_dtype):
                    new_column = column.astype('float')
                elif is_string_dtype(new_dtype):
                    new_column = column.astype('str')
                elif is_datetime_dtype(new_dtype):
                    raise make_invalid_column_type_change_error(
                        column_header,
                        old_dtype,
                        new_dtype
                    )
                elif is_timedelta_dtype(new_dtype):
                    raise make_invalid_column_type_change_error(
                        column_header,
                        old_dtype,
                        new_dtype
                    )
            if is_int_dtype(old_dtype):
                if is_bool_dtype(new_dtype):
                    new_column = column.astype('bool')
                elif is_int_dtype(new_dtype):
                    pass
                elif is_float_dtype(new_dtype):
                    new_column = column.astype('float')
                elif is_string_dtype(new_dtype):
                    new_column = column.astype('str')
                elif is_datetime_dtype(new_dtype):
                    new_column = pd.to_datetime(
                        column, 
                        unit='s',
                        errors='coerce'
                    )
                elif is_timedelta_dtype(new_dtype):
                    new_column = pd.to_timedelta(
                        column, 
                        unit='s',
                        errors='coerce'
                    )
            elif is_float_dtype(old_dtype):
                if is_bool_dtype(new_dtype):
                    new_column = column.astype('bool')
                elif is_int_dtype(new_dtype):
                    new_column = column.astype('int')
                elif is_float_dtype(new_dtype):
                    pass
                elif is_string_dtype(new_dtype):
                    new_column = column.astype('str')
                elif is_datetime_dtype(new_dtype):
                    new_column = pd.to_datetime(
                        column, 
                        unit='s',
                        errors='coerce'
                    )
                elif is_timedelta_dtype(new_dtype):
                    new_column = pd.to_timedelta(
                        column, 
                        unit='s',
                        errors='coerce'
                    )
            elif is_string_dtype(old_dtype):
                if is_bool_dtype(new_dtype):
                    new_column = to_boolean_series(new_column)
                elif is_int_dtype(new_dtype):
                    new_column = to_number_series(column).astype('int')
                elif is_float_dtype(new_dtype):
                    new_column = to_number_series(column)
                elif is_string_dtype(new_dtype):
                    pass
                elif is_datetime_dtype(new_dtype):
                    # Guess the datetime format to the best of Pandas abilities
                    datetime_format = get_datetime_format(column)
                    # If it's None, then infer_datetime_format is enough to figure it out
                    if datetime_format is not None:
                        new_column = pd.to_datetime(
                            column,
                            format=datetime_format,
                            errors='coerce'
                        )
                    else:
                        new_column = pd.to_datetime(
                            column,
                            infer_datetime_format=True,
                            errors='coerce'
                        )
                elif is_timedelta_dtype(new_dtype):
                    new_column = pd.to_timedelta(
                        column,
                        errors='coerce'
                    )
            elif is_datetime_dtype(old_dtype):
                if is_bool_dtype(new_dtype):
                    new_column = ~column.isnull()
                elif is_int_dtype(new_dtype):
                    new_column = column.astype('int') / 10**9
                elif is_float_dtype(new_dtype):
                    # For some reason, we have to do all the conversions at once
                    new_column = column.astype('int').astype('float') / 10**9
                elif is_string_dtype(new_dtype):
                    # NOTE: this is the same conversion that we send to the frontend
                    new_column = column.dt.strftime('%Y-%m-%d %X')
                elif is_datetime_dtype(new_dtype):
                    pass
                elif is_timedelta_dtype(new_dtype):
                    raise make_invalid_column_type_change_error(
                        column_header,
                        old_dtype,
                        new_dtype
                    )
            elif is_timedelta_dtype(old_dtype):
                if is_bool_dtype(new_dtype):
                    new_column = ~column.isnull()
                elif is_int_dtype(new_dtype):
                    new_column = column.dt.total_seconds().astype('int')
                elif is_float_dtype(new_dtype):
                    new_column = column.dt.total_seconds()
                elif is_string_dtype(new_dtype):
                    new_column = column.astype('str')
                elif is_datetime_dtype(new_dtype):
                    raise make_invalid_column_type_change_error(
                        column_header,
                        old_dtype,
                        new_dtype
                    )
                elif is_timedelta_dtype(new_dtype):
                    pass

            # We update the column, as well as the type of the column
            post_state.dfs[sheet_index][column_header] = new_column
            post_state.column_type[sheet_index][column_header] = get_mito_type(new_column)
            
            # We check if there are formula columns that rely on this type, and log if
            # so, so that know if this is an issue folks run into
            if len(post_state.column_evaluation_graph[sheet_index][column_header]) > 0:
                log(
                    'change_column_dtype_column_has_dependents',
                    {
                        'column_header': column_header
                    }
                )

            return post_state, None
        except:
            raise make_invalid_column_type_change_error(
                column_header,
                old_dtype,
                new_dtype
            )
        

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_header: str,
        old_dtype: str,
        new_dtype: str
    ) -> List[str]:
        df_name = post_state.df_names[sheet_index]
        column = prev_state.dfs[sheet_index][column_header]

        conversion_code = f'{df_name}[\'{column_header}\']'
        if is_bool_dtype(old_dtype):
            if is_bool_dtype(new_dtype):
                pass
            elif is_int_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'int\')'
            elif is_float_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'float\')'
            elif is_string_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'str\')'
            elif is_datetime_dtype(new_dtype):
                raise make_invalid_column_type_change_error(
                    column_header,
                    old_dtype,
                    new_dtype
                )
            elif is_timedelta_dtype(new_dtype):
                raise make_invalid_column_type_change_error(
                    column_header,
                    old_dtype,
                    new_dtype
                )
        elif is_int_dtype(old_dtype):
            if is_bool_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'bool\')'
            elif is_int_dtype(new_dtype):
                pass
            elif is_float_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'float\')'
            elif is_string_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'str\')'
            elif is_datetime_dtype(new_dtype):
                conversion_code = f'pd.to_datetime({df_name}[\'{column_header}\'], unit=\'s\', errors=\'coerce\')'
            elif is_timedelta_dtype(new_dtype):
                conversion_code = f'pd.to_timedelta({df_name}[\'{column_header}\'], unit=\'s\', errors=\'coerce\')'
        elif is_float_dtype(old_dtype):
            if is_bool_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'bool\')'
            elif is_int_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'int\')'
            elif is_float_dtype(new_dtype):
                pass
            elif is_string_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'str\')'
            elif is_datetime_dtype(new_dtype):
                conversion_code = f'pd.to_datetime({df_name}[\'{column_header}\'], unit=\'s\', errors=\'coerce\')'
            elif is_timedelta_dtype(new_dtype):
                conversion_code = f'pd.to_timedelta({df_name}[\'{column_header}\'], unit=\'s\', errors=\'coerce\')'
        elif is_string_dtype(old_dtype):
            if is_bool_dtype(new_dtype):
                conversion_code = f'to_boolean_series({df_name}[\'{column_header}\'])'
            elif is_int_dtype(new_dtype):
                conversion_code = f'to_number_series({df_name}[\'{column_header}\']).astype(\'int\')'
            elif is_float_dtype(new_dtype):
                conversion_code = f'to_number_series({df_name}[\'{column_header}\'])'
            elif is_string_dtype(new_dtype):
                pass
            elif is_datetime_dtype(new_dtype):
                # Guess the datetime format to the best of Pandas abilities
                datetime_format = get_datetime_format(column)
                if datetime_format is not None:
                    conversion_code = f'pd.to_datetime({df_name}[\'{column_header}\'], format=\'{datetime_format}\', errors=\'coerce\')'
                else:
                    conversion_code = f'pd.to_datetime({df_name}[\'{column_header}\'], infer_datetime_format=True, errors=\'coerce\')'
            elif is_timedelta_dtype(new_dtype):
                conversion_code = f'pd.to_timedelta({df_name}[\'{column_header}\'], errors=\'coerce\')'
        elif is_datetime_dtype(old_dtype):
            if is_bool_dtype(new_dtype):
                conversion_code = f'~{df_name}[\'{column_header}\'].isnull()'
            elif is_int_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'int\') / 10**9'
            elif is_float_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'int\').astype(\'float\') / 10**9'
            elif is_string_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].dt.strftime(\'%Y-%m-%d %X\')'
            elif is_datetime_dtype(new_dtype):
                pass
            elif is_timedelta_dtype(new_dtype):
                raise make_invalid_column_type_change_error(
                    column_header,
                    old_dtype,
                    new_dtype
                )
        elif is_timedelta_dtype(old_dtype):
            if is_bool_dtype(new_dtype):
                conversion_code = f'~{df_name}[\'{column_header}\'].isnull()'
            elif is_int_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].dt.total_seconds().astype(\'int\')'
            elif is_float_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].dt.total_seconds()'
            elif is_string_dtype(new_dtype):
                conversion_code = f'{df_name}[\'{column_header}\'].astype(\'str\')'
            elif is_datetime_dtype(new_dtype):
                raise make_invalid_column_type_change_error(
                    column_header,
                    old_dtype,
                    new_dtype
                )
            elif is_timedelta_dtype(new_dtype):
                pass

        return [f'{df_name}[\'{column_header}\'] = {conversion_code}']

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_header: str,
        old_dtype: str,
        new_dtype: str,
        df_names=None,
        **params
    ) -> str:
        return f'Changed {column_header} from {old_dtype} to {new_dtype}'