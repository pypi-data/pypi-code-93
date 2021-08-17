#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

setup(
    name='hanlp_downloader',
    version='0.0.24',
    description='A tool and library to save large files by creating multiple connections, '
                'modified from pget by Halil Ozercan.',
    # author='Halil Ozercan',
    # author_email='halilozercan@gmail.com',
    # url='https://github.com/halilozercan/pget',
    # download_url='https://github.com/halilozercan/pget/tarball/0.5.0',
    install_requires=['requests'],
    packages=find_packages(exclude=("tests", "tests.*")),
)
