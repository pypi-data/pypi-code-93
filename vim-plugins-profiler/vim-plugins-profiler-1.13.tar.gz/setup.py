#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

from pathlib import Path
from setuptools import setup

name = 'vim-plugins-profiler'
module = name.replace('-', '_')
here = Path(__file__).resolve().parent

setup(
    name=name,
    version='1.13',
    description='Program to output sorted summary of vim plugin startup times',
    long_description=here.joinpath('README.md').read_text(),
    long_description_content_type="text/markdown",
    url='https://github.com/bulletmark/{}'.format(name),
    author='Mark Blakeney',
    author_email='mark.blakeney@bullet-systems.net',
    keywords='vim gvim',
    license='GPLv3',
    py_modules=[module],
    python_requires='>=3.5',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        ('share/{}'.format(name), ['README.md']),
    ],
    entry_points={
        'console_scripts': ['{}={}:main'.format(name, module)],
    },
)
