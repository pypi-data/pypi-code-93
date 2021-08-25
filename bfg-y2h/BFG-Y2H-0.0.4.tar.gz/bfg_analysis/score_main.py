#!/usr/bin/env python3.7
import glob
import pandas as pd
import os
import numpy as np
import argparse
# Author: Roujia Li
# email: Roujia.li@mail.utoronto.ca

"""
Process output from read count
In each folder (yAD*DB*), take the read counts files (up/dn rawcounts and combined counts)
"""

# global variables
# conditions = ["Baseline", "H2O2", "MMS", "PoorCarbon"]

def read_files(arguments):
    """
    read csv files from input_dir,
    Input dir contains all by all (or AD*DB*) folders (ex. yAD1DB4)
    Inside each subfolder, there are counts files which are needed for calculating IS
    """
    all_csv_files = glob.glob(f"{arguments.input}/*/*_combined_counts.csv")
    # extract all folder names
    all_groups = list(set([os.path.dirname(i).split("/")[-1] for i in all_csv_files]))
    for g in all_groups: # for each AD/DB combination, get their GFP pre|med|high files
        count_files = [f for f in all_csv_files if g in f]
        if len(count_files) < 3:
            raise ValueError("Need at least 3 counts files for calculating scores")
        # pass combined counts file for processing
        pre = [s for s in count_files if "_GFP_pre_" in s][0]
        med = [s for s in count_files if "_GFP_med_" in s][0]
        high = [s for s in count_files if "_GFP_high_" in s][0]
        
        calculate_IS(pre, med, high, arguments.preFloor, arguments.weight)


def calculate_IS(GFP_pre, GFP_med, GFP_high, preFloor, weightHigh):
    """
    Input files contains a list of file paths for a specific AD and DB combination
    Required: GFP_pre, GFP_med, GFP_high
    """
    # DB as colnames and AD as row names
    # load three matrix
    GFP_pre = pd.read_csv(GFP_pre, index_col=0)
    GFP_med = pd.read_csv(GFP_med, index_col=0)
    GFP_high = pd.read_csv(GFP_high, index_col=0)

    # calculate marginal frequencies for GFP_pre
    GFP_pre_ADfreq, GFP_pre_DBfreq = marginal_freq(GFP_pre)
    # floor values in AD and DB
    GFP_pre_ADfreq = GFP_pre_ADfreq.clip(lower=preFloor)
    GFP_pre_DBfreq = GFP_pre_DBfreq.clip(lower=preFloor)
    # rebuild matrix from two vectors
    freq_mx = np.outer(GFP_pre_ADfreq, GFP_pre_DBfreq)
    GFP_pre_freq = pd.DataFrame(data = freq_mx, columns = GFP_pre_DBfreq.index.tolist(), index = GFP_pre_ADfreq.index.tolist())
    # calculate frequencies for GFP_med and GFP_high
    GFP_med_freq = freq(GFP_med)
    GFP_high_freq = freq(GFP_high)
    # use GFP_pre, med and high to calculate IS
    IS = ((weightHigh * GFP_high_freq) + GFP_med_freq) / GFP_pre_freq
    print(IS)
    #score normalization
    IS_norm = IS.sub(IS.median(axis=1), axis=0).sub(IS.median(axis=0), axis=1)
    # first normalize with AD
    IS_norm = IS_norm.apply(

# help functions
def normalization(vector):
    """
    Normalize scores in this vector
    """
    pass


def freq(matrix):

    # sum of matrix
    total = matrix.values.sum()
    freq_df = matrix / total
    return freq_df


def marginal_freq(matrix):
    # sum of matrix
    total = matrix.values.sum()
    col_freq = matrix.sum(axis=0)/total
    row_freq = matrix.sum(axis=1)/total
    return row_freq, col_freq


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='BFG-Y2H (scoring)')

    # parameters for cluster
    parser.add_argument("--input", help="Path to all read count files you want to analyze")
    #parser.add_argument("--output", help="Output path for sam files")
    #parser.add_argument("--mode", help="pick yeast or human or virus or hedgy", required=True)

    #parser.add_argument("--alignment", action="store_true", help= "turn on alignment")
    parser.add_argument("--summary", help="path to all summary files", default="/home/rothlab/rli/02_dev/08_bfg_y2h/bfg_data/summary/")
    #parser.add_argument("--ref", help="path to all reference files", default="/home/rothlab/rli/02_dev/08_bfg_y2h/bfg_data/reference/")
    #parser.add_argument("--readCount", action="store_true", help= "turn on read counting")

    # arguments with default values set
    parser.add_argument("--preFloor", type=float, help="assign floor value for GFP pre marginal frequencies", default=0.00001)
    parser.add_argument("--weight", type=float, help="weight for GFP_high", default=1)
    parser.add_argument("--rank", type=int, help="final rank to pick", default=2)
    args = parser.parse_args()
    read_files(args)
