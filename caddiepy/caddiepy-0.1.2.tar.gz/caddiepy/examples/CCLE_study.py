from caddiepy.file_utils.download_file import download_file_ftp, unzip
from caddiepy.file_utils.load_file import load_csv, load_xlsx
from caddiepy import api as api
from caddiepy.task import Task
from pathlib import Path
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import logging

logger = logging.getLogger(__name__)

CTRPV2_DATASET = 'https://ctd2-data.nci.nih.gov/Public/Broad/CTRPv2.0_2015_ctd2_ExpandedDataset/CTRPv2.0_2015_ctd2_ExpandedDataset.zip'
CTRPV2_DATASET_FILENAME = 'CTRPv2.0_2015_ctd2_ExpandedDataset.zip'
CTRPV2_RESPONSE_CURVES = f'{CTRPV2_DATASET_FILENAME[:4]}/v20.data.curves_post_qc.txt'
CTRPV2_COMPOUNDS = f'{CTRPV2_DATASET_FILENAME[:4]}/v20.meta.per_compound.txt'
CTRPV2_EXPERIMENT = f'{CTRPV2_DATASET_FILENAME[:4]}/v20.meta.per_experiment.txt'
CTRPV2_CELL_LINES = f'{CTRPV2_DATASET_FILENAME[:4]}/v20.meta.per_cell_line.txt'

CCLE_MUTATIONS = 'https://ndownloader.figshare.com/files/27902118'
CCLE_MUTATIONS_FILENAME = 'CCLE_mutations.csv'

CCLE_CELL_LINES = 'https://depmap.org/portal/download/api/download?file_name=ccle_legacy_data%2Fcell_line_annotations%2FCCLE_sample_info_file_2012-10-18.txt&bucket=depmap-external-downloads'
CCLE_CELL_LINES_FILENAME = 'sample_info.csv'
