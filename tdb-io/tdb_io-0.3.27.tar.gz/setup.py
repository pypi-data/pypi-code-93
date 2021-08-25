#!/usr/bin/env python
import os
from setuptools import setup, find_packages
#
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#exec(open('version.py').read())

import os.path

def readver(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in readver(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="tdb_io",
    description="Automatically created environment for python package",
    author="jaromrax",
    author_email="jaromrax@gmail.com",
    licence="GPL2",
    version=get_version("tdb_io/version.py"),
    #packages=find_packages(),
    packages=['tdb_io'],
    package_data={'tdb_io': ['data/*']},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    scripts = ['bin/tdb_io'],
    install_requires = ['pymongo','matplotlib','argparse','pandas','numpy','datetime','fire'],
)
#
#   To RECOVER AND ACCESS THE Data later in module: :
#  X DATA_PATH = pkg_resources.resource_filename('tdb_io', 'data/')
#  X DB_FILE =   pkg_resources.resource_filename('tdb_io', 'data/file')
#   DB_FILE = pkg_resources.resource_filename(
#       pkg_resources.Requirement.parse('nuphy2'),
#       'data/nubase2016.txt'
#   )
#   pip install -e .
#   bumpversion patch minor major release
#      release needed for pypi
