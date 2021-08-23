#!/usr/bin/env python

from setuptools import setup

setup(
    name='hoodat_utils',
    packages=['hoodat_utils'],
    version='0.0.1',
    license='MIT',
    description=
    'Utilities for hoodat',
    author='Eugene Brown',
    author_email='efbbrown@gmail.com',
    url='https://github.com/efbbrown/hoodat_utils',
    install_requires=[
        'pickle',
        'matplotlib',
        'sqlalchemy',
        'numpy',
        'scikit-learn',
        'pandas',
        'boto3'
    ],
    # download_url="https://github.com/efbbrown/hoodat_utils/archive/v.0.0.1-alpha.tar.gz",
    include_package_data=True)