import boto3
import base64
import os
import subprocess
from phcli.ph_max_auto import define_value as dv
from phcli.ph_max_auto.ph_hook.get_abs_path import get_asset_path_prefix, get_run_time
from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_aws.ph_sts import PhSts


def copy_asset_data(kwargs):

    result_path_prefix = kwargs['result_path_prefix']
    asset_path_prefix = get_asset_path_prefix(kwargs)
    run_time = get_run_time()
    ls_cmd = "aws s3 ls " + result_path_prefix
    source_file_path_keys = os.popen(ls_cmd).readlines()
    for source_file_path_key in source_file_path_keys:
        source_file_path_key = source_file_path_key.lstrip("                           PRE ").rstrip("\n")
        if '_asset' in source_file_path_key:
            asset_path = asset_path_prefix + source_file_path_key + run_time + "/"
            result_path = result_path_prefix + source_file_path_key
            cp_cmd = ["aws", "s3", "sync", result_path, asset_path]
            subprocess.call(cp_cmd)


if __name__ == '__main__':
    kwargs = {
        'path_prefix': 's3://ph-max-auto/2020-08-11/data_matching/refactor/runs/',
        'result_path_prefix': 's3://ph-max-auto/2020-08-11/data_matching/refactor/runs/manual__2021-01-18T04:49:20.117595+00:00/cleaning_data_normalization/',
        'dag_name': 'test_dag',
        'name': 'test_job',
        'run_id': 'test_run_id'
    }
    copy_asset_data(kwargs)
