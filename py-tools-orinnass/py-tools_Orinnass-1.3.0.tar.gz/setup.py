#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages
from tools import __version__, __name__

setup(
    name=__name__,
    version=__version__,
    download_url="https://gitlab.com/Orinnass/python-module-tools",
    packages=find_packages(include=('tools',))
)
