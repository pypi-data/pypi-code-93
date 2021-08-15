#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Contains an analysis with the import steps for tutorial v3
"""

MITO_TUTORIAL_CHECKPOINT_2 = {
    'name': 'checkpoint2',
    'saved_analysis': {
        "version": "0.1.96", 
        "steps": {
            "1": {
                "step_version": 1, 
                "step_type": "simple_import", 
                "file_names": ["AMTRAK-Stations-2010.csv", "Zipcode-Data-2010.csv"],
            }
        }
    }
}
