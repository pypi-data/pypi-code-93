#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.
# Distributed under the terms of the Modified BSD License.

"""
Preprocessing occurs to data that is imported into the sheet, and occurs
to _any_ data that is input into the mitosheet - they always occur, and
require no user input. 

For this reason, we take special care to preserve the backwards 
compatability of this step - as all future steps may be reliant on
transformations that have bene made.  

Each pre-processing step has an execution function, and a 
transpilation function, and are run in the same order as
they appear in the list below.
"""

from mitosheet.preprocessing.preprocess_read_file_paths import PREPROCESS_READ_FILE_PATH
from mitosheet.preprocessing.preprocess_rename_headers import PREPROCESS_RENAME_HEADERS
from mitosheet.preprocessing.preprocess_check_args_type import PREPROCESS_CHECK_ARGS_TYPE
from mitosheet.preprocessing.preprocess_copy import PREPROCESS_COPY

# NOTE: these should be in the order you want to apply them to the arguments
PREPROCESS_STEPS = [
   # First, we make sure all the args are the right type
   PREPROCESS_CHECK_ARGS_TYPE,
   # Then, we copy the args to make sure we don't change them accidently
   PREPROCESS_COPY,
   # First, we read in the files
   PREPROCESS_READ_FILE_PATH,
   # Then, we fix up their headers
   PREPROCESS_RENAME_HEADERS
]