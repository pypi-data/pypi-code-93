#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
See mito/mitosheet/steps/README.md for more information about 
how to add a step!
"""

from typing import Dict, List
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.step_performers.pivot import PivotStepPerformer
from mitosheet.step_performers.filter import FilterStepPerformer
from mitosheet.step_performers.sort import SortStepPerformer
from mitosheet.step_performers.column_steps.reorder_column import ReorderColumnStepPerformer
from mitosheet.step_performers.column_steps.add_column import AddColumnStepPerformer
from mitosheet.step_performers.column_steps.set_column_formula import SetColumnFormulaStepPerformer
from mitosheet.step_performers.merge import MergeStepPerformer
from mitosheet.step_performers.column_steps.delete_column import DeleteColumnStepPerformer
from mitosheet.step_performers.column_steps.rename_column import RenameColumnStepPerformer
from mitosheet.step_performers.column_steps.change_column_dtype import ChangeColumnDtypeStepPerformer
from mitosheet.step_performers.import_steps.simple_import import SimpleImportStepPerformer
from mitosheet.step_performers.dataframe_steps.dataframe_delete import DataframeDeleteStepPerformer
from mitosheet.step_performers.dataframe_steps.dataframe_duplicate import DataframeDuplicateStepPerformer
from mitosheet.step_performers.dataframe_steps.dataframe_rename import DataframeRenameStepPerformer

# All steps must be listed in this variable.
STEP_PERFORMERS: List[StepPerformer] = [
    PivotStepPerformer,
    ReorderColumnStepPerformer,
    FilterStepPerformer,
    SortStepPerformer,
    AddColumnStepPerformer,
    SetColumnFormulaStepPerformer,
    ChangeColumnDtypeStepPerformer,
    MergeStepPerformer,
    DeleteColumnStepPerformer,
    RenameColumnStepPerformer,
    SimpleImportStepPerformer,
    DataframeDeleteStepPerformer,
    DataframeDuplicateStepPerformer,
    DataframeRenameStepPerformer,
]

# A helpful mapping for looking up steps based on the incoming events
EVENT_TYPE_TO_STEP_PERFORMER: Dict[str, StepPerformer] = {
    step_performer.step_event_type(): step_performer
    for step_performer in STEP_PERFORMERS
}

# We also build a useful lookup mapping for the step type to step object
STEP_TYPE_TO_STEP_PERFORMER: Dict[str, StepPerformer] = {
    step_performer.step_type(): step_performer
    for step_performer in STEP_PERFORMERS
}