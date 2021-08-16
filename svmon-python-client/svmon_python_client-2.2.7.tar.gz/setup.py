#!/usr/bin/python
# -*- coding: UTF-8 -*-
from setuptools import setup

setup(
name='svmon_python_client',
version='2.2.7',
packages=['svmon_client'],
scripts=['svmon'],
package_data={'' : ['*.json','*.pem']},
description='This is a python implementation of SVMON client',
long_description=open('README.rst').read(),
author='Jie Yuan',
author_email='jie.yuan@kit.edu',
maintainer='Agustin Pane',
maintainer_email='agustin.pane@kit.edu',
license='MIT License',
platforms=["all"],
install_requires=[
  'python-dotenv',
  'requests',
],
url='https://gitlab.eudat.eu/EUDAT-TOOLS/SVMON/pysvmon',
classifiers=[
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: Implementation',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries' ]
)
