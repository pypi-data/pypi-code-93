#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='hoodat_utils',
    packages=['hoodat_utils'],
    version='0.0.2',
    license='MIT',
    description=
    'Utilities for hoodat',
    author='Eugene Brown',
    author_email='efbbrown@gmail.com',
    url='https://github.com/efbbrown/hoodat_utils',
    install_requires=requirements,
    # download_url="https://github.com/efbbrown/hoodat_utils/archive/v.0.0.1-alpha.tar.gz",
    include_package_data=True)
