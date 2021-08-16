#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    raise NotImplementedError(
        """Nextcode SDK does not support Python versions older than 3.6"""
    )

root_dir = 'nextcodecli'


def get_version_string():
    with open(os.path.join(root_dir, 'VERSION')) as version_file:
        return version_file.readlines()[0].strip()


version = get_version_string()
if 'SETUP_BRANCH' in os.environ:
    version += "-%s" % os.environ['SETUP_BRANCH']

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nextcode-cli',
    python_requires=">=3.6",
    version=version,
    description="WuXi Nextcode commandline utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='WUXI NextCODE',
    author_email='support@wuxinextcode.com',
    url='https://www.wuxinextcode.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'nextcodecli': ['VERSION', 'PUBLIC_KEY']},
    install_requires=[
        'boto3',
        'click',
        'python-dateutil==2.8.0',
        'PyYAML',
        'requests',
        'tabulate',
        'hjson',
        'PyJWT==1.7.1',
        'configparser',
        'future',
        'jsonpath_rw',
        'simplejson',
        'nextcode-sdk>=1.16.1',
    ],
    entry_points={
        'console_scripts': [
            'nextcode = nextcodecli.__main__:cli',
        ]
    },
)
