# coding=utf-8
from setuptools import setup, find_packages
import os
import sys

PACKAGE = "gyerpsdkcore"
NAME = "gy-erp-sdk-core"
DESCRIPTION = "gy erp api Python sdk."
AUTHOR = "Steven"
AUTHOR_EMAIL = "qianggao7@gmail.com"
URL = "https://github.com/stevenQiang"

TOPDIR = os.path.dirname(__file__) or "."
VERSION = __import__(PACKAGE).__version__

desc_file = open("README.md")

try:
    LONG_DESCRIPTION = desc_file.read()
finally:
    desc_file.close()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="cc",
    url=URL,
    keywords=["管易云", "sdk", "erp"],
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    platforms="any",
    python_requires='>=3'
)
