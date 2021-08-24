from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="tetest-python",
    version="1.1.0",
    author="lu, chen-zhi",
    author_email="",
    keywords="tetest python",
    description="Python Framework.",
    license="ISC",
    url="",
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[
            'requests>=2.22.0', 
            'xmltodict>=0.12.0' 
    ],
    zip_safe=True,
)