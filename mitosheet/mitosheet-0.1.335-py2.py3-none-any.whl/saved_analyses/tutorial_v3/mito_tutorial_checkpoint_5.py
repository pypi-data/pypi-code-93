#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
for tutorial v3
"""

MITO_TUTORIAL_CHECKPOINT_5 = {
    'name': 'checkpoint5',
    'saved_analysis': {
        "version": "0.1.96",
        "steps": {
            "1": {
                "step_version": 1,
                "step_type": "simple_import",
                "file_names": [
                    "AMTRAK-Stations-2010.csv",
                    "Zipcode-Data-2010.csv"
                ]
            },
            "2": {
                "step_version": 1,
                "step_type": "merge",
                "sheet_index_one": 0,
                "merge_key_one": "Zip",
                "selected_columns_one": [
                    "State",
                    "Checked_Bags",
                    "Zip"
                ],
                "sheet_index_two": 1,
                "merge_key_two": "Zip",
                "selected_columns_two": [
                    "Median_Income",
                    "Zip"
                ]
            },
            "3": {
                "step_version": 1,
                "step_type": "dataframe_rename",
                "sheet_index": 2,
                "old_dataframe_name": "df3",
                "new_dataframe_name": "Data"
            },
            "4": {
                "step_version": 1,
                "step_type": "add_column",
                "sheet_index": 2,
                "column_header": "E"
            },
            "5": {
                "step_version": 1,
                "step_type": "rename_column",
                "sheet_index": 2,
                "old_column_header": "E",
                "new_column_header": "Accepts_Bags"
            },
            "6": {
                "step_version": 1,
                "step_type": "set_column_formula",
                "sheet_index": 2,
                "column_header": "Accepts_Bags",
                "new_formula": "=IF(Checked_Bags=='Y', 1, 0)",
                "old_formula": "=0"
            }
        }
    }
}



