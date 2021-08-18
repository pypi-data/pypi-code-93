#!/usr/bin/env python

from setuptools import setup, find_packages

DESCRIPTION = ("Allows for proper decoding of datetime values contained in "
               "JSON streams")
LONG_DESCRIPTION = open('README.rst').read()

setup(
    name='sts-json-datetime',
    version='0.0.8',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='TJ Bindseil',
    author_email='tjbindseil@gmail.com',
    url="https://github.com/tbindseil/sts-mono-repo",
    license='ISC',
    platforms=["any"],
    packages=find_packages(),
    test_suite="jsondatetime.tests",
    requires=[],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    )
