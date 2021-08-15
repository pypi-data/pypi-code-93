# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='common_util_py',
    version='0.0.7',
    description='common python utility modules',
    #long_description=readme,
    long_description='common python utility modules',
    author='Jason Wee',
    author_email='peichieh@gmail.com',
    url='https://github.com/jasonwee/common-util-py',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'pymysql',
    ],
    test_suite = 'nose.collector',
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
    ],
)
