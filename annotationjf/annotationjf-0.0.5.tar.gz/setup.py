#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='annotationjf',
    version='0.0.5',
    author='jun',
    author_email='jh2259@cam.ac.uk',
    description='annotation',
    packages=['annotationjf'],
    url='https://github.com/ss-lab-cancerunit/cobra',
    install_requires=['pandas','pybiomart','setuptools'],
    include_package_data=True,
    package_data={
        'annotationjf': ['data/*'],
    },
    entry_points={
        'console_scripts': [
            'merge=annotation:merge',
        ]
    }
)
