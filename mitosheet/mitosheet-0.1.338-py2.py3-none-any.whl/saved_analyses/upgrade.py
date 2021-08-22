#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Contains functions for upgrading analyses!

NOTE: when adding a specific function for upgrading one version of a step to the other, the
format of the function should be:

def upgrade_<old_step_type>_<old_step_version>_to_<new_step_type>_<new_step_version>(step):
    ....
"""

from mitosheet.saved_analyses.schema_utils import upgrade_saved_analysis_format_to_steps_data
from mitosheet._version import __version__


def upgrade_group_1_to_pivot_2(step):
    """
    Upgrades from a group 1 step to a pivot 2 step, simply
    by changing the names of the params.

    Old format of the step: {
        "step_version": 1, 
        "step_type": "group", 
        "sheet_index": x, 
        "group_rows": [...], 
        "group_columns": [...], 
        "values": {...: ...}}}
    }

    New format of the step: {
        "step_version": 2, 
        "step_type": "pivot", 
        "sheet_index": old['sheet_index'], 
        "pivot_rows": old['group_rows'], 
        "pivot_columns": old['group_columns'], 
        "values": old['values']
    }
    """
    return {
        'step_version': 2,
        'step_type': 'pivot',
        'sheet_index': step['sheet_index'],
        'pivot_rows': step['group_rows'],
        'pivot_columns': step['group_columns'],
        'values': step['values']
    }
def upgrade_pivot_2_to_pivot_3(step):
    """
    Upgrades from a pivot 2 step to a pivot 3 step, which simple
    changes the formats of the values key to be a list rather than
    a single element

    Old format of the step: {
        "step_version": 2, 
        "step_type": "pivot", 
        "sheet_index": int, 
        "group_rows": string[], 
        "group_columns": string[], 
        "values": {string: AggregationType}
    }

    New format of the step: {
        "step_version": 3, 
        "step_type": "pivot", 
        "sheet_index": old['sheet_index'], 
        "pivot_rows": old['pivot_rows'], 
        "pivot_columns": old['pivot_columns'], 
        "values": {string: AggregationType[]} <- note the single item in this list is the previous single value
    }
    """
    return {
        'step_version': 3,
        'step_type': 'pivot',
        'sheet_index': step['sheet_index'],
        'pivot_rows': step['pivot_rows'],
        'pivot_columns': step['pivot_columns'],
        'values': {
            column_header: [aggregationType] for column_header, aggregationType in step['values'].items()
        }
    }


def upgrade_add_column_1_to_add_column_2(step): 
    """
    Upgrades from a add column 1 step to a add column 2 step, simply
    by adding the column_header_index param

    We just set the column_header_index to -1, so that it gets added to the 
    end of the dataframe, just like all previous analyses expect.

    Old format of the step: {
        "step_version": 1, 
        "step_type": "add_column", 
        'sheet_index', 
        'column_header'
    }

    New format of the step: {
        "step_version": 2, 
        "step_type": "add_column", 
        'sheet_index', 
        'column_header', 
        'column_header_index'
    }
    """
    return {
        "step_version": 2, 
        "step_type": "add_column", 
        'sheet_index': step['sheet_index'],
        'column_header': step['column_header'],
        'column_header_index': -1 # we set the column_header_index to -1 so that it gets added to the end
    }


def update_filter_column_1_to_filter_column_2(step): 
    """
    Upgrades from a filter column version 1 step to version 2. This was
    part of the refactor that unified type handling across the codebase,
    and got rid of an old distinction between a mito column type and a filter
    type. Now, we just have mito types!

    Old format of the step: {
        "step_version": 1, 
        "step_type": "filter_column", 
        "sheet_index": 0, 
        "column_header": "A", 
        "filters": [
            {"type": "number", "condition": "greater", "value": 1}, 
            {"filters": [
                {"type": "number", "condition": "greater", "value": 2}, 
                {"type": "number", "condition": "greater", "value": 3}], 
                "operator": "And"}
            ], 
        "operator": "And"}
    }

    New version of the step: {
        "step_version": 1, 
        "step_type": "filter_column", 
        "sheet_index": 0, 
        "column_header": "A", 
        "filters": [
            {"type": "number", "condition": "greater", "value": 1}, 
            {"filters": [
                {"type": "number", "condition": "greater", "value": 2}, 
                {"type": "number", "condition": "greater", "value": 3}], 
                "operator": "And"}
            ], 
        "operator": "And"}
    }

    Anywhere it says "type", we change from:
    - number -> number_series
    - string -> string_series
    - datetime -> datetime_series
    """
    type_mapping = {
        'string': 'string_series',
        'number': 'number_series',
        'datetime': 'datetime_series',
    }

    new_filters = []

    for filter_or_group in step['filters']:
        # We check if this is a filter or a group, and 
        # case appropriately!
        if 'filters' in filter_or_group:
            # Filter group case
            group = filter_or_group
            new_filters_in_group = []
            for filter_ in group['filters']:
                filter_['type'] = type_mapping[filter_['type']]
                new_filters_in_group.append(filter_)
            group['filters'] = new_filters_in_group

            new_filters.append(filter_or_group)
        else:
            # Just a regular filter, so rename for clarity
            filter_ = filter_or_group
            filter_['type'] = type_mapping[filter_['type']]
            new_filters.append(filter_)

    return {
        "step_version": 2, 
        "step_type": "filter_column", 
        "sheet_index": step['sheet_index'], 
        "column_header": step['column_header'], 
        "filters": new_filters, 
        "operator": step['operator']
    }

def upgrade_merge_1_to_merge_2(step): 
    """
    Upgrades from a merge 1 step to a merge 2 step, simply
    by adding the how param

    We just set the how param to 'lookup' 

    Old format of the step: {
        'step_version': 1, 
        'step_type': "merge", 
        'params': {
            'sheet_index_one': 0
            'merge_key_one': 'A'
            'selected_columns_one': ['A', 'B', 'C']
            'sheet_index_two': 1
            'merge_key_two': 'A'
            'selected_columns_two': ['A', 'D']
        }
    }

    New format of the step: {
        'step_version': 1, 
        'step_type': "merge",
        'params': {
            'how': 'lookup'
            'sheet_index_one': 0
            'merge_key_one': 'A'
            'selected_columns_one': ['A', 'B', 'C']
            'sheet_index_two': 1
            'merge_key_two': 'A'
            'selected_columns_two': ['A', 'D']
        }
    }
    """

    params = step['params']
    # Add the how field to the params object and set it to 'lookup'
    params['how'] = 'lookup'

    return {
        "step_version": 2, 
        "step_type": "merge", 
        "params": params
    }



"""
STEP_UPGRADES_FUNCTION_MAPPING mapping contains a mapping of all steps that need to be upgraded. A step
x at version y needs to be upgraded if STEP_UPGRADES[x][y] is defined, and in fact 
this mapping contains the function that can be used to do the upgrade!
 
NOTE: upgrades of steps should form a linear graph of upgrades to the most up to date
version. For example, if we change add_column from version 1 to version 2 to version 3, 
this object should contain:
    {
        'add_column': {
            1: upgrade_add_column_1_to_add_column_2,
            2: upgrade_add_column_2_to_add_column_3
        }
    }
"""
STEP_UPGRADES_FUNCTION_MAPPING_OLD_FORMAT = {
    'group': {
        1: upgrade_group_1_to_pivot_2
    }, 
    'pivot': {
        2: upgrade_pivot_2_to_pivot_3
    },
    'add_column': {
        1: upgrade_add_column_1_to_add_column_2
    },
    'filter_column': {
        1: update_filter_column_1_to_filter_column_2
    }
}

STEP_UPGRADES_FUNCTION_MAPPING_NEW_FORMAT = {
    'merge': {
        1: upgrade_merge_1_to_merge_2
    }
}



def is_prev_version(version: str, curr_version: str=__version__):
    """
    Returns True if the passed version is a previous version compared
    to the current version; note that this assumes semantic versioning
    with x.y.z!
    """
    old_version_parts = version.split('.')
    curr_version_parts = curr_version.split('.')

    for old_version_part, curr_version_part in zip(old_version_parts, curr_version_parts):
        if int(old_version_part) > int(curr_version_part):
            # E.g. if we have 0.2.11 and 0.1.11, we want to return early as it's clearly not older!
            return False

        if int(old_version_part) < int(curr_version_part):
            return True

    return False


def upgrade_step_to_current(step, step_upgrade_function_mapping):
    """
    A recursive helper function that, given a step, keeps upgrading it
    until it cannot be upgraded anymore

    Takes a step_upgrade_function_mapping as input, which can either be 
    STEP_UPGRADES_FUNCTION_MAPPING_OLD_FORMAT or STEP_UPGRADES_FUNCTION_MAPPING_NEW_FORMAT
    """
    step_version = step['step_version']
    step_type = step['step_type']

    if step_type in step_upgrade_function_mapping:
        step_upgrades = step_upgrade_function_mapping[step_type]
        if step_version in step_upgrades:
            return upgrade_step_to_current(step_upgrades[step_version](step), step_upgrade_function_mapping)
    
    return step

def upgrade_steps_for_old_format(saved_analysis):
    """
    A helper function that operates on the old analysis format of:
    {
        "version": "0.1.197",
        "steps": {
            1: ...
        }
    }

    And makes sure all their steps are up to date.
    """
    if saved_analysis is None:
        return None

    # If it's already in the new format, then don't worry about it
    if 'steps' not in saved_analysis and 'steps_data' in saved_analysis:
        return saved_analysis
        
    version = saved_analysis["version"]
    steps = saved_analysis["steps"]

    if not is_prev_version(version):
        # TODO: do we want to _change_ the version this was saved with? I think it doesn't
        # really matter, as it gets changed when it gets rewritten...
        return saved_analysis

    new_steps = []
    for step_idx, step in steps.items():
        new_steps.append(upgrade_step_to_current(step, STEP_UPGRADES_FUNCTION_MAPPING_OLD_FORMAT))

    # Convert the new steps in the correct format
    new_steps_json = {
        str(i + 1): step for i, step in enumerate(new_steps)
    }

    return {
        'version': __version__,
        'steps': new_steps_json
    }

def upgrade_steps_for_new_format(saved_analysis):
    """
    A helper function that operates on the new analysis format of:

    "version": "0.1.197",
    "steps_data": [
        {
            "step_version": 1,
            "step_type": "filter",
            "params": {
                ....
            }
        }
    ]

    And makes sure all their steps are up to date.
    """
    if saved_analysis is None:
        return None
        
    version = saved_analysis["version"]
    steps_data = saved_analysis["steps_data"]

    new_steps_data = []
    for step in steps_data:
        new_steps_data.append(upgrade_step_to_current(step, STEP_UPGRADES_FUNCTION_MAPPING_NEW_FORMAT))

    return {
        'version': __version__,
        'steps_data': new_steps_data
    }

def upgrade_saved_analysis_to_current_version(saved_analysis):
    """
    Upgrades a saved analysis to the current version.
    
    Notable, changes to the saved analysis take two types:
    1. Changes to the format of the saved analysis itself. 
    2. Changes to the format of the specific steps in the saved analysis.

    See mitosheet/upgrade/schemas.py, but as we only have 1 format change
    in the saved analyses, we process the specific step upgrades first if
    they exist.
    """
    saved_analysis = upgrade_steps_for_old_format(saved_analysis)
    new_format_saved_analysis = upgrade_saved_analysis_format_to_steps_data(saved_analysis)
    saved_analysis = upgrade_steps_for_new_format(new_format_saved_analysis)

    return saved_analysis
    