#!/usr/bin/env python3.7

import argparse
import logging
import logging.config
import os
import glob
import re
from bfg_analysis import alignment
from bfg_analysis import read_counts

# Author: Roujia Li
# email: Roujia.li@mail.utoronto.ca

# set global variable
###################################

# Padding sequences used
# Padding sequences are the same for human and yeast
# DB down tags
DB_Dn1 = "TCGATAGGTGCGTGTGAAGG"
DB_Dn2 = "CCTCAGTCGCTCAGTCAAG"
# DB up tags
DB_Up1 = "CCATACGAGCACATTACGGG"
DB_Up2 = "CTAACTCGCATACCTCTGATAAC"

# AD down tags
AD_Dn1 = "CTCCAGGGTTAGGCAGATG"
AD_Dn2 = "CAATCGCACTATCCCGCTG"
# AD up tags
AD_Up1 = "CCCTTAGAACCGAGAGTGTG"
AD_Up2 = "CACTCCGTTCGTCACTCAATAA"

###################################

def check_args(arguments):

    # make output dir if it doesn't exist
    if not os.path.isdir(arguments.output):
        os.mkdir(arguments.output)

    if not os.path.isdir(arguments.fastq):
        raise NotADirectoryError(f"Cannot find dir: {arguments.fastq}")

    if not os.path.isdir(arguments.summary):
        raise NotADirectoryError(f"Cannot find dir: {arguments.summary}")

    if not os.path.isdir(arguments.ref):
        raise NotADirectoryError(f"Cannot find dir: {arguments.ref}")


def main(arguments):

    check_args(arguments)
    # fastq files will be provided IF and ONLY IF we are doing alignment
    # if no alignment is required and r1, r2 is provided
    # we will skip to read counts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, "data/logging.conf")
    logging.config.fileConfig(config_file, disable_existing_loggers=False)
    log = logging.getLogger("root")
    
    # get abs path of output dir
    output_master = os.path.abspath(arguments.output)

    # gor through fastq files in the input folder
    all_fastq = glob.glob(f"{arguments.fastq}/*.fastq.gz")
    if all_fastq == []:
        raise FileNotFoundError("NO FASTQ.GZ FILES FOUND IN THE INPUT FOLDER!")
    for f in all_fastq:
        # read 1 is AD and read 2 is DB
        if not "_R1" in os.path.basename(f):
            # ignore R2
            continue
        # extract sample name
        # assume all input fastq follow the same pattern: y|hAD*DB*_GFP_(pre|med|high)_R1_*.fastq.gz
        regex = re.compile("(^.*_GFP_(pre|med|high))_.*.fastq.gz")
        ad_base = regex.match(os.path.basename(f)).group(1)
        #ad_base = os.path.basename(f).split("_")[0]

        # find DB
        db = [i for i in all_fastq if "_R2" in i and ad_base in i][0]
        # db = os.path.join(arguments.fastq, db)

        # process AD and DB to extract group information
        # this depends on the input mode
        AD_GROUP, DB_GROUP, AD_REF, DB_REF = parse_input_files(arguments.mode, ad_base, arguments.ref)
        
        # assume all the fastq files have the filename: y/hAD*DB*_GFP_*
        output_dir_name = ad_base.split("_GFP_")[0]+"/"
        output_dir = os.path.join(output_master, output_dir_name)
        if not os.path.isdir(output_dir):
            os.system("mkdir -p "+output_dir)

        # make sh dir to save submission scripts
        sh_dir = os.path.join(output_master, "GALEN_jobs")
        if not os.path.isdir(sh_dir):
            os.system("mkdir -p "+sh_dir)

        r1_csv, r2_csv = "N", "N"
        # if user wants to do alignments
        if arguments.alignment:
            r1_csv, r2_csv, sh_file = alignment.bowtie_align(f, db, AD_REF, DB_REF, output_dir, sh_dir)
            # submit job and wait
            # with r1_csv and r2_csv, add python command for read counts
            # read count script
            rc_script = os.path.join(current_dir, "read_counts.py")
            rc_cmd = f"{rc_script} -r1 {r1_csv} -r2 {r2_csv} --AD_GROUP {AD_GROUP} --DB_GROUP {DB_GROUP} --mode {arguments.mode} " \
                     f"--cutoff {arguments.cutOff} -o {output_dir} --summary {arguments.summary}"
            with open(sh_file, "a") as f:
                f.write(rc_cmd+"\n")
            os.system(f"sbatch {sh_file}")

        else:
            # retrieve r1_csv and r2_csv
            for f in os.listdir(output_dir):
                # go through the output dir and find the csv files
                if ad_base in f:
                    if "_R1_" in f and ".csv" in f and not f.endswith("counts.csv"):
                        r1_csv = os.path.join(output_dir, f)
                    if "_R2_" in f and ".csv" in f and not f.endswith("counts.csv"):
                        r2_csv = os.path.join(output_dir, f)
            # check r1 and r2
            if not os.path.isfile(r1_csv) or not os.path.isfile(r2_csv):
                continue
                #raise FileNotFoundError("Alignment script did not finish properly, check log")
            # make sh file for r1 and r2 csv files 
            # write header to sh_dir
            header = f"#!/bin/bash\n#SBATCH --time=1:00:00\n#SBATCH --job-name={ad_base}\n#SBATCH --error={os.path.join(sh_dir, ad_base)}-%j.log\n#SBATCH --mem=2G\n#SBATCH --output={os.path.join(sh_dir, ad_base)}-%j.log\n"
            sh_file = os.path.join(sh_dir, f"{ad_base}_rc.sh")
            rc_script = os.path.join(current_dir, "read_counts.py")
            rc_cmd = f"{rc_script} -r1 {r1_csv} -r2 {r2_csv} --AD_GROUP {AD_GROUP} --DB_GROUP {DB_GROUP} --mode {arguments.mode} " \
                     f"--cutoff {arguments.cutOff} -o {output_dir} --summary {arguments.summary}"
            with open(sh_file, "a") as f:
                f.write(header)
                f.write(rc_cmd+"\n")
            print(ad_base) 
            os.system(f"sbatch {sh_file}")

            #read_counts.RCmain(r1_csv, r2_csv, AD_GROUP, DB_GROUP, arguments.mode, output_dir, arguments.cutOff, arguments.summary)



def parse_input_files(mode, ad_base, ref_path):
    """
    This function is customized to read different input files and assign them different reference sequences
    Currently we can take yeast/human/virus/hedgy
    **** Please make sure the fastq filenames have the following format ****
    Input filename format:
    For yeast: yAD(1-9|M|all)DB(1-9|M|all) - 1-9 means group, M stands for Miha, all stands for all groups. e.g yAD1DBall means AD group 1 x DB all
    For human: hAD(0-9)DB(0-9), numbers stands for pooling groups. e.g hAD1DB4 means AD group 1 x DB group 4,
    For virus: h|v(AD(0-9|NC|2u|all)h|v(DB(0-9|NC|2u|all)), numbers stands for pooling groups, e.g hAD4vDBNC, human AD group 4 vs virus DBNC
    For hedgy:
    """
    ###################################
    # Directory to store all the reference sequences
    hREF_PATH = os.path.join(ref_path, "h_ref/")
    yREF_PATH = os.path.join(ref_path, "y_ref/")
    # added for virus
    hvREF_PATH = os.path.join(ref_path, "hv_ref/")
    vREF_PATH = os.path.join(ref_path, "v_ref/")
    # added for hedgy
    heREF_PATH = os.path.join(ref_path, "h_hedgy/")

    if mode == "yeast":
        m = re.match(r"yAD([1-9]|M|all)DB([1-9]|M|all)", ad_base)

        AD_GROUP = "G"+m.group(1)
        DB_GROUP = "G"+m.group(2)

        AD_REF = yREF_PATH + "y_AD_wnull_" + AD_GROUP
        DB_REF = yREF_PATH + "y_DB_wnull_" + DB_GROUP

    elif mode == "human":
        m = re.match(r"hAD([0-9]+)DB([0-9]+)", ad_base)
        if int(m.group(1)) <10:
            AD_GROUP = "G0"+m.group(1)
        else:
            AD_GROUP = "G"+m.group(1)
        if int(m.group(2)) <10:
            DB_GROUP = "G0"+m.group(2)
        else:
            DB_GROUP = "G"+m.group(2)
        AD_REF = hREF_PATH + "h_AD_" + AD_GROUP
        DB_REF = hREF_PATH + "h_DB_" + DB_GROUP

    elif mode == "virus":
        # human vs virus pairwise
        m = re.match(r"([hv])(AD([0-9]+)|ADNC|AD2u|ADall)([hv])(DB([0-9]+)|DBNC|DB2u|DBall)", ad_base)

        if not m.group(3) is None:
            if int(m.group(3)) < 10:
                AD_GROUP = "AD_wnull_G"+m.group(3)
            else:
                AD_GROUP = "AD_wnull_G"+m.group(3)
        else:
            AD_GROUP = m.group(2)

        if not m.group(6) is None:
            if int(m.group(6)) <10:
                DB_GROUP = "DB_wnull_G"+m.group(6)
            else:
                DB_GROUP = "DB_wnull_G"+m.group(6)
        else:
            DB_GROUP = m.group(5)

        if m.group(1) == "v": #virus
            AD_REF = vREF_PATH + "v_" + AD_GROUP
        else:
            AD_REF = hvREF_PATH + "h_" + AD_GROUP

        if m.group(4) == "v": # virus
            DB_REF = vREF_PATH + "v_" + DB_GROUP
        else:
            DB_REF = hvREF_PATH + "h_" + DB_GROUP

    elif mode == "hedgy":

        m = re.match(r"hAD([0-9]+)DBhe", ad_base)
        if int(m.group(1)) <10:
            AD_GROUP = "G0"+m.group(1)
        else:
            AD_GROUP = "G"+m.group(1)

        DB_GROUP = "hedgy"

        AD_REF = hvREF_PATH + "h_AD_wnull_" + AD_GROUP
        DB_REF = heREF_PATH + "h_DB_" + DB_GROUP

    else:
        raise ValueError("Please provide valid mode: yeast, human, virus or hedgy")

    return AD_GROUP, DB_GROUP, AD_REF, DB_REF


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='BFG-Y2H')

    # parameters for cluster
    parser.add_argument("--fastq", help="Path to all fastq files you want to analyze")
    parser.add_argument("--output", help="Output path for sam files")
    parser.add_argument("--mode", help="pick yeast or human or virus or hedgy", required=True)

    parser.add_argument("--alignment", action="store_true", help= "turn on alignment")
    parser.add_argument("--summary", help="path to all summary files", default="/home/rothlab/rli/02_dev/08_bfg_y2h/bfg_data/summary/")
    parser.add_argument("--ref", help="path to all reference files", default="/home/rothlab/rli/02_dev/08_bfg_y2h/bfg_data/reference/")
    #parser.add_argument("--readCount", action="store_true", help= "turn on read counting")
    parser.add_argument("--cutOff", type=int, help = "assign cut off", default=20)

    args = parser.parse_args()
    main(args)
