# -*- coding: utf-8 -*-
from setuptools import setup

# Longer description
readme = ('Library for Digital Linear Filters (DLF) as used, for instance, '
          'in Geophysics for electromagnetic modelling. See '
          'https://github.com/emsig/libdlf')

setup(
    name="libdlf",
    version="0.1.4",
    description="Library for Digital Linear Filters (DLF)",
    long_description=readme,
    author="The emsig community",
    author_email="info@emsig.xyz",
    url="https://github.com/emsig/libdlf",
    license="CC-BY-4.0",
    packages=["libdlf"],
    include_package_data=True,
    install_requires=["numpy"],
)
