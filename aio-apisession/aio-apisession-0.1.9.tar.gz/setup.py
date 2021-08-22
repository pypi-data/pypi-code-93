# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apisession']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'aio-apisession',
    'version': '0.1.9',
    'description': '',
    'long_description': None,
    'author': 'Sebastian Acuna',
    'author_email': 'sebastian@unholster.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
