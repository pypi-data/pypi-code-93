#!/usr/bin/env python3.7
import glob
import pandas as pd
import os

# Author: Roujia Li
# email: Roujia.li@mail.utoronto.ca

"""
Process output from read count
In each folder (yAD*DB*), take the read counts files (up/dn rawcounts and combined counts)
"""

# global variables
# conditions = ["Baseline", "H2O2", "MMS", "PoorCarbon"]

def read_files(input_dir):
    """
    read csv files from input_dir,
    Input dir contains all by all (or AD*DB*) folders (ex. yAD1DB4)
    Inside each subfolder, there are counts files which are needed for calculating IS
    """
    all_csv_files = glob.glob(f"{input_dir}/*counts.csv")
    # extract all folder names
    all_groups = list(set([os.path.dirname(i) for i in all_csv_files]))
    for g in all_groups: # for each AD/DB combination, get their GFP pre|med|high files
        pass

