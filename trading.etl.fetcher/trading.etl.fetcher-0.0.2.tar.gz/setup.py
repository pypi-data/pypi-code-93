from setuptools import setup
from setuptools import find_namespace_packages
from typing import List


def requirements() -> List[str]:
    with open('requirements/base.txt', 'r') as file_handler:
        package_list = file_handler.readlines()
        package_list = [package.rstrip() for package in package_list]

    return package_list


setup(
    name='trading.etl.fetcher',
    description='Exchange OHLCV Fetcher Package used in Trading',
    author='Trading',

    version='0.0.2',

    install_requires=requirements(),
    packages=find_namespace_packages(include=[
        "trading.*",
        "trading.etl.*"
    ]),
    python_requires='>=3.7'
)
