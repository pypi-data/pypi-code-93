#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Deletes an existing saved analysis.
"""

from mitosheet.saved_analyses import delete_saved_analysis

DELETE_SAVED_ANALYSIS_UPDATE_EVENT = 'delete_analysis_update'
DELETE_SAVED_ANALYSIS_UPDATE_PARAMS = [
    'analysis_name',
]

def execute_delete_saved_analysis_update(
        steps_manager,
        analysis_name,
    ):
    """
    This function deletes the saved analysis from the user's .mito folder
    """ 
    delete_saved_analysis(analysis_name)
    

DELETE_SAVED_ANALYSIS_UPDATE = {
    'event_type': DELETE_SAVED_ANALYSIS_UPDATE_EVENT,
    'params': DELETE_SAVED_ANALYSIS_UPDATE_PARAMS,
    'execute': execute_delete_saved_analysis_update
}