#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.


from copy import deepcopy
import functools
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.state import State
from numbers import Number
from typing import Any, Dict, List, Optional
import pandas as pd
from datetime import date

from mitosheet.sheet_functions.types import (
    BOOLEAN_SERIES,
    DATETIME_SERIES,
    NUMBER_SERIES,
    STRING_SERIES
)
from mitosheet.errors import (
    make_no_sheet_error,
    make_no_column_error,
    make_invalid_filter_error
)

# SOME CONSTANTS USED IN THE FILTER STEP ITSELF
FC_EMPTY = 'empty'
FC_NOT_EMPTY = 'not_empty'
SHARED_FILTER_CONDITIONS = [
    FC_EMPTY,
    FC_NOT_EMPTY
]

FC_BOOLEAN_IS_TRUE = 'boolean_is_true'
FC_BOOLEAN_IS_FALSE = 'boolean_is_false'
BOOLEAN_FILTER_CONDITIONS = [
    FC_BOOLEAN_IS_TRUE,
    FC_BOOLEAN_IS_FALSE
]

FC_STRING_CONTAINS = 'contains'
FC_STRING_DOES_NOT_CONTAIN = 'string_does_not_contain'
FC_STRING_EXACTLY = 'string_exactly'
FC_STRING_NOT_EXACTLY = 'string_not_exactly'
STRING_FILTER_CONDITIONS = [
    FC_STRING_CONTAINS,
    FC_STRING_DOES_NOT_CONTAIN,
    FC_STRING_EXACTLY,
    FC_STRING_NOT_EXACTLY
]

FC_NUMBER_EXACTLY = 'number_exactly'
FC_NUMBER_NOT_EXACTLY = 'number_not_exactly'
FC_NUMBER_GREATER = 'greater'
FC_NUMBER_GREATER_THAN_OR_EQUAL = 'greater_than_or_equal'
FC_NUMBER_LESS = 'less'
FC_NUMBER_LESS_THAN_OR_EQUAL = 'less_than_or_equal'
NUMBER_FILTER_CONDITIONS = [
    FC_NUMBER_EXACTLY,
    FC_NUMBER_NOT_EXACTLY,
    FC_NUMBER_GREATER,
    FC_NUMBER_GREATER_THAN_OR_EQUAL,
    FC_NUMBER_LESS,
    FC_NUMBER_LESS_THAN_OR_EQUAL
]

FC_DATETIME_EXACTLY = 'datetime_exactly'
FC_DATETIME_GREATER = 'datetime_greater'
FC_DATETIME_GREATER_THAN_OR_EQUAL = 'datetime_greater_than_or_equal'
FC_DATETIME_LESS = 'datetime_less'
FC_DATETIME_LESS_THAN_OR_EQUAL = 'datetime_less_than_or_equal'
DATETIME_FILTER_CONDITIONS = [
    FC_DATETIME_EXACTLY,
    FC_DATETIME_GREATER,
    FC_DATETIME_GREATER_THAN_OR_EQUAL,
    FC_DATETIME_LESS,
    FC_DATETIME_LESS_THAN_OR_EQUAL,
]

class FilterStepPerformer(StepPerformer):
    """
    Allows you to filter a column based on some conditions and some values. 
    """

    @classmethod
    def step_version(cls) -> int:
        return 2

    @classmethod
    def step_type(cls) -> str:
        return 'filter_column'

    @classmethod
    def step_display_name(cls) -> str:
        return 'Filtered a Column'
    
    @classmethod
    def step_event_type(cls) -> str:
        return 'filter_column_edit'

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        """
        Saturates the filter event with a `has_non_empty_filter` - which is useful
        for for logging
        """
        has_non_empty_filter = False
        for filter_or_group in params['filters']:
            if 'filters' in filter_or_group:
                # If it's a group
                if len(filter_or_group['filters']) > 0:
                    has_non_empty_filter = True
            else:
                # If it's a single filter
                has_non_empty_filter = True

        params['has_non_empty_filter'] = has_non_empty_filter
        return params

    @classmethod
    def execute(
        cls,
        prev_state: State,
        sheet_index: int,
        column_header: str,
        operator: str,
        filters,
        **params
    ) -> State:
        # if the sheet doesn't exist, throw an error
        if not prev_state.does_sheet_index_exist_within_state(sheet_index):
            raise make_no_sheet_error(sheet_index)

        # We check that the filtered column exists 
        missing_column = set([column_header]).difference(prev_state.column_metatype[sheet_index].keys())
        if len(missing_column) > 0: 
            raise make_no_column_error(missing_column)

        # If no errors we create a new step for this filter
        post_state = deepcopy(prev_state)

        # Execute the filter
        post_state.dfs[sheet_index] = _execute_filter(
            prev_state.dfs[sheet_index], 
            column_header,
            operator,
            filters
        )

        # keep track of which columns are filtered
        post_state.column_filters[sheet_index][column_header]['operator'] = operator
        post_state.column_filters[sheet_index][column_header]['filters'] = filters

        return post_state, None

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        execution_data: Optional[Dict[str, Any]],
        sheet_index: int,
        column_header: str,
        operator: str,
        filters,
        **params
    ) -> List[str]:
        df_name = post_state.df_names[sheet_index]

        filter_strings = []
        for filter_or_group in filters:
            # If it is a group, we build the code for each filter, and then combine them at the end
            if 'filters' in filter_or_group:
                group_filter_strings = []
                for filter_ in filter_or_group['filters']:
                    group_filter_strings.append(
                        get_filter_string(df_name, column_header, filter_)
                    )

                filter_strings.append(
                    # Note: we add parens around this, so it's grouped properly
                    "(" + combine_filter_strings(filter_or_group['operator'], group_filter_strings) + ")"
                )
            else:
                filter_strings.append(
                    get_filter_string(df_name, column_header, filter_or_group)
                )

        if len(filter_strings) == 0:
            return []
        elif len(filter_strings) == 1:
            return [
                f'{df_name} = {df_name}[{filter_strings[0]}]',
                f'{df_name} = {df_name}.reset_index(drop=True)'
            ]
        else:
            filter_string = combine_filter_strings(operator, filter_strings, split_lines=True)
            return [
                f'{df_name} = {df_name}[{filter_string}]',
                f'{df_name} = {df_name}.reset_index(drop=True)'
            ]

    @classmethod
    def describe(
        cls,
        sheet_index: int,
        column_header: str,
        operator: str,
        filters,
        df_names=None,
        **params
    ) -> str:
        if df_names is not None:
            df_name = df_names[sheet_index]
            return f'Filtered {column_header} in {df_name}'
        return f'Filtered {column_header}'


def get_applied_filter(df, column_header, filter_):
    """
    Given a filter triple, returns the filter indexes for that
    actual dataframe
    """
    type_ = filter_['type']
    condition = filter_['condition']
    value = filter_['value']

    # First, we case on the shared conditions, to get them out of the way
    if condition in SHARED_FILTER_CONDITIONS:
        if condition == FC_EMPTY:
            return df[column_header].isna()
        elif condition == FC_NOT_EMPTY:
            return df[column_header].notnull()
    
    if type_ == BOOLEAN_SERIES:
        if condition not in BOOLEAN_FILTER_CONDITIONS:
            raise Exception(f'Invalid condition passed to boolean filter {condition}')

        if condition == FC_BOOLEAN_IS_TRUE:
            return df[column_header] == True
        elif condition == FC_BOOLEAN_IS_FALSE:
            return df[column_header] == False
    elif type_ == STRING_SERIES:
        if condition not in STRING_FILTER_CONDITIONS:
            raise Exception(f'Invalid condition passed to string filter {condition}')

        # Check that the value is the valid
        if not isinstance(value, str):
            raise make_invalid_filter_error(value, STRING_SERIES)

        if condition == FC_STRING_CONTAINS:
            return df[column_header].str.contains(value, na=False)
        if condition == FC_STRING_DOES_NOT_CONTAIN:
            return ~df[column_header].str.contains(value, na=False)
        elif condition == FC_STRING_EXACTLY:
            return df[column_header] == value
        elif condition == FC_STRING_NOT_EXACTLY:
            return df[column_header] != value

    elif type_ == NUMBER_SERIES:
        if condition not in NUMBER_FILTER_CONDITIONS:
            raise Exception(f'Invalid condition passed to number filter {condition}')
        
        # Check that the value is the valid
        if not isinstance(value, Number):
            raise make_invalid_filter_error(value, NUMBER_SERIES)

        if condition == FC_NUMBER_EXACTLY:
            return df[column_header] == value
        elif condition == FC_NUMBER_NOT_EXACTLY:
            return df[column_header] != value
        elif condition == FC_NUMBER_GREATER:
            return df[column_header] > value
        elif condition == FC_NUMBER_GREATER_THAN_OR_EQUAL:
            return df[column_header] >= value
        elif condition == FC_NUMBER_LESS:
            return df[column_header] < value
        elif condition == FC_NUMBER_LESS_THAN_OR_EQUAL:
            return df[column_header] <= value

    elif type_ == DATETIME_SERIES:
        if condition not in DATETIME_FILTER_CONDITIONS:
            raise Exception(f'Invalid condition passed to datetime filter {condition}')

        # Check that we were given something that can be understood as a date
        try:
            timestamp = pd.to_datetime(value)
        except:
            # If we hit an error, because we restrict the input datetime, 
            # this is probably occuring because the user has only partially input the date, 
            # and so in this case, we just default it to the minimum possible timestamp for now!
            timestamp = date.min

        if condition == FC_DATETIME_EXACTLY:
            return df[column_header] == timestamp
        elif condition == FC_DATETIME_GREATER:
            return df[column_header] > timestamp
        elif condition == FC_DATETIME_GREATER_THAN_OR_EQUAL:
            return df[column_header] >= timestamp
        elif condition == FC_DATETIME_LESS:
            return df[column_header] < timestamp
        elif condition == FC_DATETIME_LESS_THAN_OR_EQUAL:
            return df[column_header] <= timestamp
    else:
        raise Exception(f'Invalid type passed in filter {type_}')

def combine_filters(operator, filters):

    def filter_reducer(filter_one, filter_two):
        # helper for combining filters based on the operations
        if operator == 'Or':
            return (filter_one) | (filter_two)
        elif operator == 'And':
            return (filter_one) & (filter_two)
        else:
            raise Exception(f'Operator {operator} is unsupported')

    # Combine all the filters into a single filter
    return functools.reduce(filter_reducer, filters)

def _execute_filter(
        df, 
        column_header,
        operator,
        filters
    ):
    """
    Executes a filter on the given column, filtering by removing any rows who
    don't meet the condition.
    """

    applied_filters = []

    for filter_or_group in filters:

        # If it's a group, then we build the filters for the group, combine them
        # and then add that to the applied filters
        if 'filters' in filter_or_group:
            group_filters = []
            for filter_ in filter_or_group['filters']:
                group_filters.append(
                    get_applied_filter(df, column_header, filter_)
                )

            if len(group_filters) > 0:
                applied_filters.append(
                    combine_filters(filter_or_group['operator'], group_filters)
                )    

        # Otherwise, we just get that specific filter, and append it
        else:
            applied_filters.append(get_applied_filter(df, column_header, filter_or_group))    
    
    if len(applied_filters) > 0:
        return df[combine_filters(operator, applied_filters)].reset_index(drop=True)
    else:
        return df


def get_filter_string(df_name, column_header, filter_):
    """
    Transpiles a specific filter to a fitler string, to be used
    in constructing the final transpiled code
    """
    condition = filter_['condition']
    value = filter_['value']

    FILTER_FORMAT_STRING_DICT = {
        # SHARED CONDITIONS
        FC_EMPTY: '{df_name}.{column_header}.isna()',
        FC_NOT_EMPTY: '{df_name}.{column_header}.notnull()',

        # BOOLEAN
        FC_BOOLEAN_IS_TRUE: '{df_name}[\'{column_header}\'] == True',
        FC_BOOLEAN_IS_FALSE: '{df_name}[\'{column_header}\'] == False',

        # NUMBERS
        FC_NUMBER_EXACTLY: '{df_name}[\'{column_header}\'] == {value}',
        FC_NUMBER_NOT_EXACTLY: '{df_name}[\'{column_header}\'] != {value}',
        FC_NUMBER_GREATER: '{df_name}[\'{column_header}\'] > {value}',
        FC_NUMBER_GREATER_THAN_OR_EQUAL: '{df_name}[\'{column_header}\'] >= {value}',
        FC_NUMBER_LESS: '{df_name}[\'{column_header}\'] < {value}',
        FC_NUMBER_LESS_THAN_OR_EQUAL: '{df_name}[\'{column_header}\'] <= {value}',
        
        # STRINGS
        FC_STRING_CONTAINS: '{df_name}[\'{column_header}\'].str.contains(\'{value}\', na=False)',
        FC_STRING_DOES_NOT_CONTAIN: '~{df_name}[\'{column_header}\'].str.contains(\'{value}\', na=False)',
        FC_STRING_EXACTLY: '{df_name}[\'{column_header}\'] == \'{value}\'',
        FC_STRING_NOT_EXACTLY: '{df_name}[\'{column_header}\'] != \'{value}\'',

        # DATES
        FC_DATETIME_EXACTLY: '{df_name}[\'{column_header}\'] == pd.to_datetime(\'{value}\')',
        FC_DATETIME_GREATER: '{df_name}[\'{column_header}\'] > pd.to_datetime(\'{value}\')',
        FC_DATETIME_GREATER_THAN_OR_EQUAL: '{df_name}[\'{column_header}\'] >= pd.to_datetime(\'{value}\')',
        FC_DATETIME_LESS: '{df_name}[\'{column_header}\'] < pd.to_datetime(\'{value}\')',
        FC_DATETIME_LESS_THAN_OR_EQUAL: '{df_name}[\'{column_header}\'] <= pd.to_datetime(\'{value}\')',            
    }

    return FILTER_FORMAT_STRING_DICT[condition].format(
        df_name=df_name,
        column_header=column_header,
        value=value
    )

def combine_filter_strings(operator, filter_strings, split_lines=False):
    """
    Combines the given filter strings with the passed operator, optionally 
    splitting the lines at 120 characters.
    
    NOTE: we choose to keep groups together for readibility, and so do not
    split the lines if we are combing a group.
    """
    if len(filter_strings) == 1:
        return filter_strings[0]
    else:
        # If there are multiple conditions, we combine them together, with the
        # given operator in the middle
        OPERATOR_SIGNS = {
            'Or': '|',
            'And': '&'
        }
        # Put parens around them
        filter_strings = [
            f'({fs})' for fs in filter_strings
        ]

        filter_string = ''
        current_line_length = 0
        for i, fs in enumerate(filter_strings):
            if i != 0:
                filter_string += f' {OPERATOR_SIGNS[operator]} '
            filter_string += fs
            # We keep track of how long the lines are, and if they go over 100 characters,
            # then we split them into a new line (not if this is the last one though)
            current_line_length += len(fs)
            if split_lines and current_line_length > 100 and i != len(filter_strings) - 1:
                filter_string += ' \\\n\t'
                current_line_length = 0

        return filter_string