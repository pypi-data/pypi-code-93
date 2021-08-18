####
# title: config.py
#
# language: Python3.8
# date: 2021-04-23
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   jinxif file name nomenclature, lab, or workplace dependent constants and fuctions are kept here
#####

# library
import os
import stat

# (CHANGE ME)
# const
es_marker_standard = {
    '53BP1',
    'AR', 'aSMA',
    'BAX','BCL2','BMP2','BMP4','BMP6',
    'CAV1','CC3','CCND1',
    'CD3','CD4','CD8','CD20','CD31','CD44','CD45','CD68','CD90',
    'CGA',
    'CK5','CK7','CK8','CK14','CK17','CK19',
    'cPARP',
    'CSF1R','ColI','ColIV','CoxIV',
    'DAPI',
    'EGFR','ER','Ecad',
    'FoxP3',
    'GATA3','gH2AX','Glut1','GRNZB',
    'H3K27','H3K4','HER2','HIF1a',
    'Ki67',
    'LamAC','LamB1','LamB2',
    'MSH2','MUC1',
    'PCNA','PD1','PDGFRa','PDL1','PDL1ab','PDL1d','PDPN','PgR','PgRc4',
    'p63','pAKT','pERK','pHH3','pRB','pS62MYC','pS6RP','panCK',
    'R0c2','R0c3','R0c4','R0c5',
    'R1c2',
    'R5Qc2','R5Qc3','R5Qc4','R5Qc5',
    'R6Qc2','R6Qc3','R6Qc4','R6Qc5',
    'R7Qc2','R7Qc3','R7Qc4','R7Qc5',
    'R8Qc2','R8Qc3','R8Qc4','R8Qc5',
    'R10Qc2','R10Qc3','R10Qc4','R10Qc5',
    'R11Qc2','R11Qc3','R11Qc4','R11Qc5',
    'R12Qc2','R12Qc3','R12Qc4','R12Qc5',
    'R13Qc2','R13Qc3','R13Qc4','R13Qc5',
    'R14Qc2','R14Qc3','R14Qc4','R14Qc5',
    'RAD51',
    'S100','SYP',
    'TUBB3',
    'Vim',
    'ZEB1',
}



# functions
def slurmbatch(
        s_pathfile_sbatch,
        s_srun_cmd,
        s_jobname = None,
        s_partition = None,
        s_gpu = None,
        s_mem = None,
        s_time = None,
        s_account = None,
    ):
    '''
    version: 2021-04-21

    input:
        s_pathfile_sbatch: path and filename of the sbatch file that is generated.
        s_srun_cmd: commandline command to be run via srun.
        s_jobname: 8 letter job name to be displayed at squeue. 
            if None, the first 8 letters form the s_pathfile_sbatch filename will be taken.
        s_partition: slurm cluster partition to use. 
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_gpu: slurm cluster gpu allocation. 
            OHSU ACC options are any 'gpu:1', faster 'gpu:v100:1', slower 'gpu:p100:1',
            not rapids compatible is 'gpu:rtx2080:1'.
        s_mem: slurm cluster memory allocation. format '64G'.
        s_time: slurm cluster time allocation in hour or day format. 
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tewaked to OHSU ACC settings.
        s_account: slurm cluster account to credit time from. 
            my OHSU ACC options are 'gray_lab', 'chin_lab', 'heiserlab'.

    output:
        executable sbatch file generated at s_pathfile_sbatch.

    description:
        generate an executable slurm sbatch file.
        this code might be very specific to the OHSU ACC exacloud cluster.
    '''
    # bash shebang
    s_batchfile = '#!/bin/bash\n'
    # partition
    if not (s_gpu is  None):
        s_partition = 'gpu'
    s_batchfile += f'#SBATCH --partition={s_partition}\n'
    # gpu
    if not (s_gpu is None):
        s_batchfile += f'#SBATCH --gres={s_gpu}\n'
    # ram
    if not (s_mem is None):
        s_batchfile += f'#SBATCH --mem={s_mem}\n'
    # time and qos
    if not (s_time is None):
        s_batchfile += f'#SBATCH --time={s_time}\n'
        if (s_time.find('-') > -1) and (float(s_time.replace('-','.')) > 1.5):
            if (s_gpu != None):
                s_qos = 'gpu_long_jobs'
            elif (float(s_time.replace('-','.')) > 10):
                s_qos = 'very_long_jobs'
            else:
                s_qos = 'long_jobs'
            # add sbatch entry
            s_batchfile += f'#SBATCH --qos={s_qos}\n'
    # account
    if not (s_account is None):
        s_batchfile += f'#SBATCH -A {s_account}\n'
    # job name
    if not (s_jobname is None):
        s_batchfile += f'#SBATCH --job-name={s_jobname}\n'
    # run dmc
    s_batchfile += f'srun {s_srun_cmd} 2>&1\n'
    # generate sbatch file
    with open(s_pathfile_sbatch, 'w') as f:
        f.write(s_batchfile)
    # make sbatch file executable for current user
    os.chmod(s_pathfile_sbatch, os.stat(s_pathfile_sbatch).st_mode | stat.S_IEXEC)  # bue: the | is a bit wise OR operator

