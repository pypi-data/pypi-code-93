#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Tradologics Python SDK
# https://tradologics.com
#
# Copyright 2020-2021 Tradologics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


def get_version():
    with open("tradologics/__init__.py") as f:
        init = f.read().replace(' ', '')
        return init.split('__version__="')[1].split('"')[0].strip()


def get_requirements():
    with open("requirements.txt") as f:
        return [line.rstrip() for line in f]


def get_description():
    with open("README.rst") as f:
        return f.read()


setup(
    name="tradologics",
    version=get_version(),
    description="Tradologics SDK",
    long_description=get_description(),
    url="https://tradologics.com",
    author="Tradologics, Inc.",
    author_email="opensource@tradologics.com",
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 4 - Beta",

        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",

        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    platforms=["any"],
    keywords="tradologics, tradologics.com",
    packages=find_packages(exclude=["contrib", "docs", "tests", "examples"]),
    install_requires=get_requirements()
)
