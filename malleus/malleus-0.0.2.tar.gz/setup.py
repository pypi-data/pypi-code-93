#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

import malleus_main

from os import path
this_directory = path.abspath(path.dirname(__file__)) 
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='malleus',
    version=malleus_main.__version__,
    packages=find_packages(),
    python_requires='>=3.0',
    author='Travis Pawlikowski',
    author_email='tnp123@protonmail.com',
    description='Toolset for Terminal Use',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/fleetyeets/malleus',
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/fleetyeets/malleus/issues',
        'Source': 'https://github.com/fleetyeets/malleus',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    entry_points = {'console_scripts': [
        'malleus=malleus_main.cli:main'],
        },
)
