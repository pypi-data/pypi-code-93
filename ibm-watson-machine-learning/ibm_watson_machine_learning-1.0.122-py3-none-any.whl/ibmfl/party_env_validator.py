"""
IBM Confidential
OCO Source Materials
5737-H76, 5725-W78, 5900-A1R
(c) Copyright IBM Corp. 2020 All Rights Reserved.
The source code for this program is not published or otherwise divested of its trade secrets,
irrespective of what has been deposited with the U.S. Copyright Office.
"""
#!/usr/bin/env python3

import logging
import importlib

from warnings import warn
import os
import sys

# Added fix for message "Using TensorFlow backend."
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')
import keras
sys.stderr = stderr


latest_required_libraries = ["tensorflow==2.4.1", "sklearn==0.23.2", "torch==1.7.1",
                             "keras==2.2.4", "numpy", "pandas", "pytest",
                             "yaml", "parse", "websockets", "jsonpickle", "requests",
                             "scipy==1.4.1", "environs", "pathlib2", "diffprivlib",
                             "psutil", "setproctitle", "tabulate", "lz4",
                             "cv2", "gym", "ray==0.8.0", "cloudpickle==1.3.0", "image"]

oldest_required_libraries = ["tensorflow==2.1.0", "sklearn==0.23.1", "torch==1.7.1",
                             "keras==2.2.4", "numpy==1.17.4", "pandas", "pytest",
                             "yaml", "parse", "websockets", "jsonpickle", "requests",
                             "scipy==1.4.1", "environs", "pathlib2", "diffprivlib",
                             "psutil", "setproctitle", "tabulate", "lz4",
                             "cv2", "gym", "ray==0.8.0", "cloudpickle==1.3.0", "image"]


for old_lib, new_lib in zip(oldest_required_libraries, latest_required_libraries):

    req_lib_new = new_lib.split("==")
    req_lib_old = old_lib.split("==")

    try:
        var = importlib.import_module(req_lib_new[0])

        if len(req_lib_old) == 2 and len(req_lib_new) == 2:
            if var.__version__ != req_lib_old[1] and var.__version__ != req_lib_new[1]:
                print("Module", req_lib_old[0], "has incompatible version:", var.__version__, "Oldest version is:", req_lib_old[1],
                      "but latest version is:", req_lib_new[1])

    except Exception as e:
        if len(req_lib_old) == 2 or len(req_lib_new) == 2:
            print(e, "Oldest version is:", req_lib_old[1], "but latest version is: ", req_lib_new[1])
        else:
            print(e)
        continue
