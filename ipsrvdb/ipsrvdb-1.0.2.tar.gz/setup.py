# coding=utf-8

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='ipsrvdb',
    version="1.0.2",
    description=(
        'IPsrv ipsrv db parsing library'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='ipsrv.net',
    author_email='admin@ipsrv.net',
    maintainer='ipsrv',
    maintainer_email='admin@ipsrv.net',
    license='Apache License Version 2.0',
    packages=['ipsrvdb'],
    platforms=["all"],
    url='https://github.com/ipsrv/ipsrvdb-python',
)
