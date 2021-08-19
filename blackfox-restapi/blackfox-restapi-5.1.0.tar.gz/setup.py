# coding: utf-8

"""
    BlackFox

    Client library for BlackFox service
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "blackfox-restapi"
VERSION = "5.1.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "certifi>=2017.4.17",
    "python-dateutil>=2.1",
    "six>=1.10",
    "urllib3>=1.23"
]
    

setup(
    name=NAME,
    version=VERSION,
    description="BlackFox rest api client",
    author="Vodena",
    author_email="",
    url="https://github.com/vodena/BlackFoxRestApiPython",
    keywords=["BlackFox"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test.*", "test"]),
    include_package_data=True,
    long_description="""\
        BlackFox python client
    """
)
