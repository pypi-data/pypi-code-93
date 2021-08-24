#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import splitext, basename
import os.path as path
from glob import glob

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
     long_description = f.read()

with open(path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

with open('LICENSE.txt') as f:
     license = f.read()

setup(name='lemmings-hpc',
    version=version,
    description='Flexible chaining of jobs on hpc with workflows',
    author='Thibault Gioud, Jimmy-John Hoste',
    author_email="coop@cerfacs.fr",
    url="",
    license ="MIT License",
    license_files = license,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["hpc","job chaining", "worfklows"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    # packages=find_packages(include=['lemmings']),
    install_requires=[
        "click",
        "prettytable>=2.0.0, <3.0",
        "numpy",
        "PyYAML",
      ],
    tests_require=[
        'pytest',
        'pytest-mock'
      ],

    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    entry_points={
        "console_scripts": ["lemmings-hpc = lemmings_hpc.cli:main"]
        }
     )
