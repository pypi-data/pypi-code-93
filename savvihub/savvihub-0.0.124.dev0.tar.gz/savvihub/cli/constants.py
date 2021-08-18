import os
from pathlib import Path

WEB_HOST = os.environ.get('SAVVIHUB_WEB_HOST', 'https://savvihub.com')

CUR_DIR = os.getcwd()
DEFAULT_SAVVI_DIR = os.path.join(str(Path.home()), '.savvihub')
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_SAVVI_DIR, 'config')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATASET_SOURCE_TYPE_SAVVIHUB_S3 = 'savvihub-s3'
DATASET_SOURCE_TYPE_AWS_S3 = 's3'
DATASET_SOURCE_TYPE_GCP_GS = 'gcp-gs'

DATASET_PATH_PARSE_SCHEME_S3_WITH_SEPERATOR = 's3://'
DATASET_PATH_PARSE_SCHEME_GS_WITH_SEPERATOR = 'gs://'
DATASET_PATH_PARSE_SCHEME_S3 = 's3'
DATASET_PATH_PARSE_SCHEME_GS = 'gs'

DATASET_VERSION_HASH_LATEST = 'latest'

PROJECT_TYPE_VERSION_CONTROL = 'version-control'
PROJECT_TYPE_CLI_DRIVEN = 'cli-driven'
