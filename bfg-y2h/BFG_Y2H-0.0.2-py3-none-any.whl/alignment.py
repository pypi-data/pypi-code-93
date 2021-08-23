#!/usr/bin/env python3.7

# Author: Roujia Li
# email: Roujia.li@mail.utoronto.ca

# Functions used for making alignment command

# import param
import os
import logging.config

align_log = logging.getLogger("alignments")

def bowtie_align(ad, db, AD_ref, DB_ref, output, sh_dir):
    """
    Align r1 and r2 to reference
    Log bowtie output 
    """
    basename = os.path.basename(ad)
    error_log = os.path.join(sh_dir, f"{basename.replace('.fastq.gz', '')}")
    bowtie_log = os.path.join(sh_dir, f"{basename.replace('.fastq.gz', '_bowtie.log')}")
    # write header to sh_dir
    header = f"#!/bin/bash\n#SBATCH --time=24:00:00\n#SBATCH --job-name={basename}\n#SBATCH " \
             f"--cores-per-socket=8\n#SBATCH --error={error_log}-%j.log\n#SBATCH --mem=10G\n#SBATCH " \
             f"--output={error_log}-%j.log\n"

    # command for AD
    params_r1 = "-q --norc --local --very-sensitive-local -t -p 8 --reorder "
    sam_file_r1 = os.path.join(output, basename.replace('.fastq.gz','_AD_BC.sam'))
    
    input_f_r1 = f"-x {AD_ref} -U {ad} -S {sam_file_r1}"
    commandr1 = f"bowtie2 {params_r1} {input_f_r1} 2> {bowtie_log}"
    # command for DB
    params_r2 = "-q --nofw --local --very-sensitive-local -t -p 8 --reorder "
    sam_file_r2 = os.path.join(output, basename.replace("_R1_", "_R2_").replace('.fastq.gz','_DB_BC.sam'))
    input_f_r2 = f"-x {DB_ref} -U {db} -S {sam_file_r2}"
    commandr2 = f"bowtie2 {params_r2} {input_f_r2} 2> {bowtie_log}"

    # sort r1_sam
    sorted_r1 = sam_file_r1.replace(".sam", "_sorted.sam")
    sort_r1 =  f"samtools sort -n -o {sorted_r1} {sam_file_r1} \n rm {sam_file_r1}"
    # sort r2_sam
    sorted_r2 = sam_file_r2.replace(".sam", "_sorted.sam")
    sort_r2 = f"samtools sort -n -o {sorted_r2} {sam_file_r2} \n rm {sam_file_r2}"

    # remove headers
    r1 = sam_file_r1.replace(".sam", "_noh.sam")
    r2 = sam_file_r2.replace(".sam", "_noh.sam")

    rm_headers_r1 = f"grep -v \"^@\" {sorted_r1} > {r1}"
    rm_headers_r2 = f"grep -v \"^@\" {sorted_r2} > {r2}"

    r1_csv = r1.replace(".sam", ".csv")
    r2_csv = r2.replace(".sam", ".csv")

    cut_csv_r1 = f"cut -f 1-5 {r1} > {r1_csv}"
    cut_csv_r2 = f"cut -f 1-5 {r2} > {r2_csv}"

    # write all commands to file for submitting jobs
    with open(os.path.join(sh_dir, f"{basename.replace('.fastq.gz', '.sh')}"), "w") as f:
        f.write(header+"\n")

        f.write(commandr1+"\n")
        f.write(sort_r1+"\n")
        f.write(rm_headers_r1+"\n")
        f.write(cut_csv_r1+"\n")

        f.write(commandr2+"\n")
        f.write(sort_r2+"\n")
        f.write(rm_headers_r2+"\n")
        f.write(cut_csv_r2+"\n")

        # remove no header sam file
        f.write(f"rm {r1}\n")
        f.write(f"rm {r2}\n")

    return r1_csv, r2_csv, os.path.join(sh_dir, f"{basename.replace('.fastq.gz', '.sh')}")


# depreciated
def bowtie_align_hap(fastq, ref, output):

    """
    align hDB to all the hDB ref
    align R1 to hDB uptag and R2 to hDB downtag
    """

    basename = os.path.basename(fastq)

    if "R1" in fastq:
        params = "-q --norc --local --very-sensitive-local -t -p 23 -k 2 --reorder "
        sam_file = basename.replace('.fastq.gz','_DB_BC_up.sam')
    elif "R2" in fastq:  
        params = "-q --nofw --local --very-sensitive-local -t -p 23 -k 2 --reorder "
        sam_file = basename.replace('.fastq.gz','_DB_BC_dn.sam')
    else:
        raise ValueError("Cannot match R1/R2 in input fastq files")

    input_f = "-x " + ref + " -U " + fastq + " -S " + os.path.join(output, sam_file)
    log_f = os.path.join(output, sam_file.replace(".sam", "_bowtie.log"))
    command = f"bowtie2 {params} {input_f} 2> {log_f}"
    os.system(command)

    return os.path.join(output, sam_file)


# if __name__ == "__main__":
#
#     parser = argparse.ArgumentParser(description='BFG-Y2H')
#     parser.add_argument("--fastq", help="Path to all fastq files you want to analyze")
#
#     args=parser.parse_args()
#
#     f = args.fastq
#     ref = "/home/rothlab/rli/02_dev/08_bfg_y2h/h_ref/h_DB_all"
#     output = "/home/rothlab/rli/02_dev/08_bfg_y2h/output/190821_hDB/hDB_test_bowtie_k/"
#
#     for fastq in os.listdir(f):
#         fastq = f+fastq
#         bowtie_align_hap(fastq, ref, output)

