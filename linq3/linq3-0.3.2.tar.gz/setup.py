from setuptools import setup, find_packages

import sys

if sys.version_info[0] != 3:
    sys.exit('Sorry, only python 3 is supported.')

with open('README.md') as f:
    long_description = f.read()

setup(
    name='linq3',
    version='0.3.2',
    packages=find_packages(exclude=['tests']),
    license='MIT',
    author='weijiang',
    description='C#-Linq-like wrapper',
    long_description=long_description,
    install_requires=[
    ],
    test_suite='nose.collector'
)
