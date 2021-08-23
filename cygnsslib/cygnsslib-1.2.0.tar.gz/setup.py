#!/usr/bin/env python3
from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as fh:
    req = fh.read()

setup(
    name='cygnsslib',
    version='1.2.0',
    author='Amer Melebari and James D. Campbell',
    author_email='amelebar@usc.edu',
    description='Toolset for working with CYGNSS data and downloading CYGNSS data from PODAAC',
    long_description=long_description,
    install_requires=req.split(),
    long_description_content_type="text/markdown",
    url='https://bitbucket.org/usc_mixil/cygnsslib',
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src", exclude='cygnsslib.data_downloader'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
