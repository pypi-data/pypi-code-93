#!/usr/bin/env python3

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()
    
setup(
  name='pyfunctest',
  version='0.0.6',
  license="MIT",
  author="Sergey Lunkov",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/Lunkov/pyfunctest",
  project_urls={
    "Bug Tracker": "https://github.com/Lunkov/pyfunctest/issues",
  },
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],  
  package_dir={'pyfunctest': 'src'},
  packages=['pyfunctest'],
  install_requires=[
    "gitpython",
    "python-dotenv",
    "docker",
    "docker-compose",
    "minio",
    "mysqlclient",
    "psycopg2",
    "pika",
    "kafka-python",
  ],
)
