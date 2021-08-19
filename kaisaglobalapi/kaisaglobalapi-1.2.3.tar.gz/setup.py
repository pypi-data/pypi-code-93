#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 KAISA FINANCIAL GROUP LTD.
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

import sys
from os.path import dirname, join

from setuptools import (
    find_packages,
    setup,
)

is_py3 = sys.version_info[0] == 3

with open(join(dirname(__file__), 'VERSION.txt'), 'rb') as f:
    version = f.read().decode('ascii').strip()

install_requires = ['requests>=2.25.1',
                    'urllib3>=1.25.8',
                    'numpy>=1.18.1',
                    'pandas>=1.1.3',
                    'websocket-client>=1.1.0',
                    'json5>=0.9.1',
                    'crypto==1.4.1']

long_description = """
    Kaisa Global Quantitative Trading API is provided.
    The correspondingly market data and trading is supported in HK market.
    see details in https://www.kaisaglobal.com/open-api
"""

setup(
    name='kaisaglobalapi',
    version=version,
    description='Kaisa Global Quantitative Trading API',
    classifiers=[],
    keywords='Kaisa Global HK Stock Quant Trading API',
    author='KAISA FINANCIAL GROUP LTD.',
    author_email='itsupport@kaisafin.com',
    url='https://www.kaisaglobal.com/open-api',
    license='Apache License 2.0',
    packages=find_packages(exclude=[]),
    package_data={'': ['*.*']},
    include_package_data=True,
    install_requires=install_requires,
    long_description=long_description
)
