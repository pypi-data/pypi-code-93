#!/usr/bin/env python
import pathlib
import sys
import os
import platform
from setuptools import setup

PKG_NAME = 'kwargshelper'
MAJOR = 1
MINOR = 2
MICRO = 1
ISRELEASED = True
VERSION = f'{MAJOR}.{MINOR}.{MICRO}'

# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
with open(HERE / "README.md") as fh:
    README = fh.read()


def getListOfFiles(dir_name):
    '''
    For the given path, get the List of all files in the directory tree 
    '''
    # create a list of file and sub directories
    # names in the given directory
    list_of_files = os.listdir(dir_name)
    all_files = list()
    # Iterate over all the entries
    for entry in list_of_files:
        # Create full path
        full_path = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(full_path):
            all_files = all_files + getListOfFiles(full_path)
        else:
            all_files.append(full_path)

    return all_files

def get_src_modules(root_path: pathlib.Path):
    dir_name = root_path / 'kwhelp'
    # Get the list of all files in directory tree at given path
    listOfFiles = getListOfFiles(dir_name)
    _slice = len(str(dir_name)) + 1
    py_lst = [f[_slice:-3] for f in list(filter(lambda p: p.endswith('.py'), listOfFiles))]
    return py_lst

MODULES = get_src_modules(HERE)


# This call to setup() does all the work
setup(
    name=PKG_NAME,
    version=VERSION,
    python_requires='>=3.6.0',
    description="Manages testing for valid kwargs key, values pairs and assigns class attributes for pairs.",
    long_description_content_type="text/markdown",
    long_description=README,
    url="https://github.com/Amourspirit/python-kwargshelper",
    author=":Barry-Thomas-Paul: Moss",
    author_email='bigbytetech@gmail.com',
    license="MIT",
    # package_dir={'kwhelp': 'kwhelp'},
    packages=['kwhelp', 'kwhelp.rules', 'kwhelp.helper'],
    py_modules=MODULES,
    keywords=['python', 'kwargs', 'args', 'parse', 'helper'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
