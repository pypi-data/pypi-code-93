#!/usr/bin/env python3.7

import pandas as pd
import logging.config
import argparse
import os
from bfg_analysis import supplements
from bfg_analysis import plot

# Author: Roujia Li
# email: Roujia.li@mail.utoronto.ca
analysis_log = logging.getLogger("analysis")


class Read_Count(object):

    def __init__(self, AD_GENES, DB_GENES, r1, r2, output_dir, sam_cutoff):
        self._r1 = r1 # sorted sam file for r1
        self._r2 = r2 # sorted sam file for r2
        self._ad_genes = AD_GENES # list of AD gene names
        self._db_genes = DB_GENES # list of DB gene names
        print(self._r1)
        print(self._r2)
        self._uptag_file = f"{r1.replace('.csv', '')}_uptag_rawcounts.csv"
        self._dntag_file = f"{r2.replace('.csv', '')}_dntag_rawcounts.csv"
        
        self._cutoff = sam_cutoff

        ####### log ########
        analysis_log.info("r1 csv file: %s", r1)
        analysis_log.info("r2 csv file: %s", r2)
        
    def _BuildMatrix(self):
        """
        Build empty up tag matrix with col = DB_size ; row = AD_size 
        Build empty dn tag matrix with col = DB_size ; row = AD_size
        """
        self._uptag_matrix = pd.DataFrame(0, index=self._ad_genes, columns=self._db_genes)
        self._dntag_matrix = pd.DataFrame(0, index=self._ad_genes, columns=self._db_genes)
        #print "Matrix build" 
        analysis_log.info("Matrix build with AD: %s, DB: %s", str(self._uptag_matrix.shape[0]), str(self._uptag_matrix.shape[1]))

    def _ReadCounts(self):
        
        f1 = open(self._r1, "r")
        f2 = open(self._r2, "r")
        
        dn_pairs = {}
        up_pairs = {}
        fail =0
        dn_count = 0
        while 1:
            
            r1_line = f1.readline() # AD
            r2_line = f2.readline() # DB
            
            if r1_line == ""  or r2_line == "":
                print("end of file")
                break

            r1_line = r1_line.strip().split()
            r2_line = r2_line.strip().split()
            # both files are sorted by name, if name is different, log error
            if r1_line[0] != r2_line[0]:
                #log error and exit
                analysis_log.error("# READ ID DOES NOT MATCH #")
                analysis_log.error("From read one (AD): %s", r1_line[0])
                analysis_log.error("From read two (DB): %s", r2_line[0])
                break

            if int(r1_line[4]) < self._cutoff or int(r2_line[4]) < self._cutoff: # check quality
                fail += 1
                continue

            if r1_line[2] == "*" or r2_line[2] =="*": # if one of the read didnt map
                fail += 1
                continue
            r1_name = r1_line[2].split(";")
            r2_name = r2_line[2].split(";")

            if r1_name[-1] == r2_name[-1]:
                if r1_name[-1] == "dn":
                    dn_count += 1
                    dn_pairs[(r2_name[1], r1_name[1])] = dn_pairs.get((r2_name[1], r1_name[1]), 0) + 1
                else:
                    up_pairs[(r2_name[1], r1_name[1])] = up_pairs.get((r2_name[1], r1_name[1]), 0) + 1

        analysis_log.info("Total reads for dn tags: %s", str(sum(dn_pairs.values())))
        analysis_log.info("Total reads for up tags: %s", str(sum(dn_pairs.values())))
        dntag_matrix = (pd.Series(dn_pairs)
                .unstack(fill_value=0)
                .T
                .reindex(index=self._dntag_matrix.index, columns=self._dntag_matrix.columns, fill_value=0))
        #print dntag_matrix.shape
        uptag_matrix = (pd.Series(up_pairs)
                .unstack(fill_value=0)
                .T
                .reindex(index=self._uptag_matrix.index, columns=self._uptag_matrix.columns, fill_value=0))
        
        f1.close()
        f2.close()
        # save to file
        dntag_matrix.to_csv(self._dntag_file)
        uptag_matrix.to_csv(self._uptag_file)
        return uptag_matrix, dntag_matrix


def RCmain(r1, r2, AD_GROUP, DB_GROUP, mode, output_dir, sam_cutoff, summary_dir):



    # set global variables
    ###################################
    # summary files are used to grep gene names, group information
    # and to create fasta reference files if needed

    # in the summary files, the following columns must exist: Group, Locus, Index, UpTag_Sequence, DnTag_Sequence

    # summary for AD (all the genes and group)
    # yeast
    yAD_summary = os.path.join(summary_dir, "20180627_byORFeome_AD.csv")
    # human
    hAD_summary = os.path.join(summary_dir, "20180927_bhORFeome_AD_RL.csv")
    # human with null
    hvAD_summary = os.path.join(summary_dir, "20180927_bhORFeome_AD_RL_withNull.csv")

    # summary for DB (all the genes and group)
    # yeast
    yDB_summary = os.path.join(summary_dir, "20180627_byORFeome_DB_AA.csv")
    # human
    hDB_summary = os.path.join(summary_dir, "20180927_bhORFeome_DB_RL.csv")
    # human with null
    hvDB_summary = os.path.join(summary_dir, "20180927_bhORFeome_DB_RL_withNull.csv")
    # hedgy summary
    heDB_summary = os.path.join(summary_dir, "20201014_hEDGY_Screen1_ORF_BC_list.csv")

    # virus
    vADNC = os.path.join(summary_dir, "vADNC_withNull.csv")
    vAD2u = os.path.join(summary_dir, "vAD2u_withNull.csv")
    vDBNC = os.path.join(summary_dir, "vDBNC_withNull.csv")
    vADall = os.path.join(summary_dir, "vADall_withNull.csv")

    # get AD and DB genes from different files based on the mode
    if mode == "yeast":
        AD_genes, DB_genes = supplements.read_summary(yAD_summary, yDB_summary, AD_GROUP, DB_GROUP)

    elif mode =="human":
        AD_genes, DB_genes = supplements.read_summary(hAD_summary, hDB_summary, AD_GROUP, DB_GROUP)

    elif mode == "virus":
        if "G" in AD_GROUP: # human
            AD_GROUP = AD_GROUP.split("_")[-1]
        if "G" in DB_GROUP: # human
            DB_GROUP = DB_GROUP.split("_")[-1]
        AD_genes, DB_genes = supplements.read_summary_virus(hvAD_summary, hvDB_summary, AD_GROUP, DB_GROUP)

    elif mode == "hedgy":
        AD_GROUP = AD_GROUP.split("_")[-1]
        AD_genes, DB_genes = supplements.read_summary_hedgy(hvAD_summary, heDB_summary, AD_GROUP)
    else:
        raise ValueError("Please pride valid mode: yeast or human orvirus")

    rc = Read_Count(AD_genes, DB_genes, r1, r2, output_dir, sam_cutoff)
    # create empty matrix
    rc._BuildMatrix()
    uptag_matrix, dntag_matrix = rc._ReadCounts()

    combined = uptag_matrix + dntag_matrix

    combined.to_csv(f"{r1.replace('.csv', '')}_combined_counts.csv")

    # plot up and dn corr
    # sample_bc_corr.png
    plot.bc_corr(r1.replace('.csv', ''), uptag_matrix, dntag_matrix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BFG-Y2H')

    # make fasta from summary file (AD and DB)
    # -- create: creates fasta file from summary.csv
    # parser.add_argument('--pfasta', help="Path to fasta file")

    # parameters for cluster
    parser.add_argument("-r1", help="Read 1 SAM file")
    parser.add_argument("-r2", help="Read 2 SAM file")
    parser.add_argument("--AD_GROUP", help="AD group number")
    parser.add_argument("--DB_GROUP", help="DB group number")
    parser.add_argument("--mode", help="Mode (yeast, human, virus, hedgy)")
    parser.add_argument("--cutoff", help="SAM reads quality cutoff", type=int)
    parser.add_argument("--summary", help="path to all summary files", default="/home/rothlab/rli/02_dev/08_bfg_y2h/bfg_data/summary/")
    parser.add_argument("-o", "--output", help="Output path")
    args = parser.parse_args()

    RCmain(args.r1, args.r2, args.AD_GROUP, args.DB_GROUP, args.mode, args.output, args.cutoff, args.summary)
