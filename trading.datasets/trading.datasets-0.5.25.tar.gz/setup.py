"""trading-datasets is a data-retrieval library for crypto asset exchanges."""

from setuptools import setup
from setuptools import find_namespace_packages
from typing import List


DOCLINES = __doc__.split('\n')


def requirements() -> List[str]:
    with open('requirements/base.txt', 'r') as file_handler:
        package_list = file_handler.readlines()
        package_list = [package.rstrip() for package in package_list]

    return package_list


setup(
    name='trading.datasets',
    description=DOCLINES[0],
    author='Trading',
    version='0.5.25',

    install_requires=requirements(),
    packages=find_namespace_packages(include=[
        "trading.*",
    ]),
    python_requires='>=3.7'
)
