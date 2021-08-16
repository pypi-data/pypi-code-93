# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 10:08:46 2020

@author: connor o'brien
"""

from setuptools import find_packages, setup

setup(
    name = 'cupidsat',
    packages = ['cupid'],
    version = '1.1.4',
    description = 'Functions for downloading and working with CuPID data',
    author = 'Connor OBrien',
    author_email = 'obrienco@bu.edu',
    license = 'MIT',
    url="https://github.com/Cupid-Cubesat/cupidsat",
    install_requires = ['numpy','spacepy','scipy','datetime','pytz','matplotlib'],
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
