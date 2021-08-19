# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name='dataverk-vault',
    version='0.1.10',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.6',
    install_requires=install_requires,
    # metadata to display on PyPI
    author="NAV IKT",
    description="Vault integration for dataverk",
    license="MIT",
    keywords="vault dataverk",
    url="https://github.com/navikt"
)
