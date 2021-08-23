#!/usr/bin/env python2
from setuptools import setup, find_packages
from distutils.util import convert_path
from distutils.command.install import INSTALL_SCHEMES
import os, sys, glob

setup(
    name                 = 'pwndbg',
    packages             = [],
    install_requires     = [],
    version              = '0.1.1',
    description          = "Go to https://pwndbg.com for installation instructions",
    author               = "Pwndbg",
    author_email         = "zachriggle@gmail.com",
    url                  = 'https://pwndbg.com',
    download_url         = "https://pwndbg.com",

    license              = "MIT",
    classifiers          = [
        'Topic :: Security',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers'
    ]
)
