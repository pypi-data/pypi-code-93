import os
from importlib_metadata import version, PackageNotFoundError

# try fetching version, if it fails (usually when in dev), add default
try:
    BIOLIB_PACKAGE_VERSION = version('pybiolib')
except PackageNotFoundError:
    BIOLIB_PACKAGE_VERSION = '0.0.0'

IS_DEV = os.getenv('BIOLIB_DEV', '').upper() == 'TRUE'

BIOLIB_PACKAGE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

BIOLIB_IS_RUNNING_IN_ENCLAVE = os.getenv('BIOLIB_IS_RUNNING_IN_ENCLAVE', '').upper() == 'TRUE'

BIOLIB_CLOUD_SKIP_PCR_VERIFICATION = os.getenv('BIOLIB_CLOUD_SKIP_PCR_VERIFICATION', '').upper() == 'TRUE'

RUN_DEV_JOB_ID = 'run-dev-mocked-job-id'
