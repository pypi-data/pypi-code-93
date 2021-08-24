# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aio_aws']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.2,<6.0',
 'aiobotocore>=1.3.0,<1.4.0',
 'aiofiles>=0.7.0,<0.8.0',
 'boto3>=1.17.42,<2.0.0',
 'botocore>=1.20.42,<2.0.0',
 'requests>=2.23.0,<3.0.0',
 'tinydb>=3.15,<4.0']

extras_require = \
{'all': ['aioredis>=1.3,<2.0', 'databases[sqlite,mysql,postgresql]'],
 'awscli': ['awscli>=1.18,<2.0'],
 'docs': ['Sphinx>=3.2,<4.0',
          'sphinx-autoapi>=1.5,<2.0',
          'sphinx-autodoc-typehints>=1.11,<2.0',
          'sphinx-rtd-theme>=0.5.0,<0.6.0',
          'ipython>=7.24.1,<8.0.0']}

setup_kwargs = {
    'name': 'aio-aws',
    'version': '0.13.6',
    'description': 'aio-aws',
    'long_description': '[![Build Status](https://travis-ci.com/dazza-codes/aio-aws.svg?branch=master)](https://travis-ci.com/dazza-codes/aio-aws)\n[![Documentation Status](https://readthedocs.org/projects/aio-aws/badge/?version=latest)](https://aio-aws.readthedocs.io/en/latest/?badge=latest)\n\n# aio-aws\n\nAsynchronous functions and tools for AWS services.  There is a\nlimited focus on s3 and AWS Batch and Lambda.  Additional services could be\nadded, but this project is likely to retain a limited focus.\nFor general client solutions, see\n[aioboto3](https://github.com/terrycain/aioboto3) and\n[aiobotocore](https://github.com/aio-libs/aiobotocore), which wrap\n[botocore](https://botocore.amazonaws.com/v1/documentation/api/latest/index.html)\n\nThe API documentation is at [readthedocs](https://aio-aws.readthedocs.io/)\n\n# Install\n\nThis project has a very limited focus.  For general client solutions, see\n[aioboto3](https://github.com/terrycain/aioboto3) and\n[aiobotocore](https://github.com/aio-libs/aiobotocore), which wrap\n[botocore](https://botocore.amazonaws.com/v1/documentation/api/latest/index.html)\nto patch it with features for async coroutines using\n[aiohttp](https://aiohttp.readthedocs.io/en/latest/) and\n[asyncio](https://docs.python.org/3/library/asyncio.html).\n\nThis project is alpha-status with a 0.x.y API version that could break.\nThere is no promise to support or develop it extensively, at this time.\n\n## pip\n\n```shell\npip install -U aio-aws[all]\npip check  # pip might not guarantee consistent packages\n```\n\n## poetry\n\npoetry will try to guarantee consistent packages or fail.\n\n```shell\n# with optional extras\npoetry add aio-aws --extras all\n```\n\n```toml\n# pyproject.toml snippet\n\n[tool.poetry.dependencies]\npython = "^3.7"\n\n# with optional extras\naio-aws = {version = "^0.1.0", extras = ["all"]}\n\n# or, to make it an optional extra\naio-aws = {version = "^0.1.0", extras = ["all"], optional = true}\n[tool.poetry.extras]\naio-aws = ["aio-aws"]\n\n```\n\n# Contributing\n\nTo use the source code, it can be cloned directly. To\ncontribute to the project, first fork it and clone the forked repository.\n\nThe following setup assumes that\n[miniconda3](https://docs.conda.io/en/latest/miniconda.html) and\n[poetry](https://python-poetry.org/docs/) are installed already\n(and `make` 4.x).\n\n- https://docs.conda.io/en/latest/miniconda.html\n    - recommended for creating virtual environments with required versions of python\n    - see https://github.com/dazza-codes/conda_container/blob/master/conda_venv.sh\n- https://python-poetry.org/docs/\n    - recommended for managing a python project with pip dependencies for\n      both the project itself and development dependencies\n\n```shell\ngit clone https://github.com/dazza-codes/aio-aws\ncd aio-aws\nconda create -n aio-aws python=3.7\nconda activate aio-aws\nmake init  # calls poetry install\nmake test\n```\n\n# License\n\n```text\nCopyright 2019-2021 Darren Weber\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n   http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n```\n\n# Notices\n\nInspiration for this project comes from various open source projects that use\nthe Apache 2 license, including but not limited to:\n- Apache Airflow: https://github.com/apache/airflow\n- aiobotocore: https://github.com/aio-libs/aiobotocore\n- botocore: https://github.com/boto/botocore\n',
    'author': 'Darren Weber',
    'author_email': 'dazza-codes@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dazza-codes/aio-aws',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
