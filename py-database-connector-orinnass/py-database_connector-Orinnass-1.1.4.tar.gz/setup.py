#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages
from database_connector import __version__, __name__


def get_install_requires():
    with open('requirements.txt', 'r') as file_req:
        lines_req = file_req.readlines()
        for index, i in enumerate(lines_req):
            if '-e' in i:
                module_name = i.split('#egg=')[1].strip()
                install_command = i.split('-e ')[1].strip()
                lines_req[index] = f'{module_name} @ {install_command}\n'
        return lines_req


setup(
    name=__name__,
    version=__version__,
    download_url="https://gitlab.com/Orinnass/python-module-database-connector",
    packages=find_packages(),
    install_requires=get_install_requires()
)
