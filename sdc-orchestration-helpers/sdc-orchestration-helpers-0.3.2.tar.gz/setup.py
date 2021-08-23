"""
    Set up the sdc_helpers package
"""
from setuptools import setup, find_packages

airflow_requires = [
    'PyYaml',
    'dag-factory',
    'PyYaml',
    'boto3>=1.16.63',
    'sagemaker',
    'sdc_helpers'
]

def get_required(file_name):
    """
        Get Required Filename during setup
    """
    with open(file_name):
        return file_name.read().splitlines()


setup(
    name='sdc-orchestration-helpers',
    packages=find_packages(exclude=("tests")),
    install_requires=[],
    extras_require={
        'airflow': airflow_requires,
    },
    description='A package of orchestration helpers and utilities for sdc orchestration.',
    version='0.3.2',
    url='https://github.com/RingierIMU/sdc-global-orchestration-helpers',
    author='Ringier South Africa',
    author_email='tools@ringier.co.za',
    keywords=['pip', 'helpers', 'airflow', 'orchestration'],
    download_url='https://github.com/RingierIMU/sdc-global-orchestration-helpers/archive/v0.1.0.zip'
)
