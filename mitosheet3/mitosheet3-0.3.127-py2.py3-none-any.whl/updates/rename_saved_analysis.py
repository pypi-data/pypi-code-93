#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Rename an existing saved analysis.
"""

from mitosheet.saved_analyses import rename_saved_analysis

RENAME_SAVED_ANALYSIS_UPDATE_EVENT = 'rename_analysis_update'
RENAME_SAVED_ANALYSIS_UPDATE_PARAMS = [
    'old_analysis_name',
    'new_analysis_name'
]

def execute_rename_saved_analysis_update(
        steps_manager,
        old_analysis_name,
        new_analysis_name
    ):
    """
    This function renames the saved analysis from the user's .mito folder
    """ 
    rename_saved_analysis(old_analysis_name, new_analysis_name)
    

RENAME_SAVED_ANALYSIS_UPDATE = {
    'event_type': RENAME_SAVED_ANALYSIS_UPDATE_EVENT,
    'params': RENAME_SAVED_ANALYSIS_UPDATE_PARAMS,
    'execute': execute_rename_saved_analysis_update
}