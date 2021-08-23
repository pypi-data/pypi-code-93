#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from gstorm import __version__

requirements = [
    # TODO: put package requirements here
    'pygqlc',
    'inflect',
    'pydash',
    'click',
    'pytz',
    'tzlocal',
    'valiotworker',
    'attrs'
]

setup_requirements = [
    # TODO: put setup requirements (distutils extensions, etc.) here
    'twine'
]

test_requirements = [
    # TODO: put package test requirements here
    'pytest',
    'pytest-cov',
    'black'
]

desc = "GraphQL ORM for python (based on pygqlc)"
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gstorm',
    version=__version__,
    description=desc,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Valiot",
    author_email="hiring@valiot.io",
    url='https://github.com/valiot/python-gstorm',
    packages=find_packages(include=['gstorm', 'gstorm.cli']),
    entry_points={
        'console_scripts': [
            'gstorm-cli=gstorm.cli.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords=['gstorm', 'orm', 'graphql', 'gql'],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
