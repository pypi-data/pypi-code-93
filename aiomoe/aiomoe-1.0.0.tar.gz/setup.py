# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiomoe', 'aiomoe.api', 'aiomoe.errors', 'aiomoe.models', 'aiomoe.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'loguru>=0.5.3,<0.6.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'aiomoe',
    'version': '1.0.0',
    'description': 'Fully asynchronous trace.moe API wrapper',
    'long_description': None,
    'author': 'FeeeeK',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
