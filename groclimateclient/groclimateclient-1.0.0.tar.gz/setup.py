# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['groclimateclient']

package_data = \
{'': ['*']}

install_requires = \
['fuzzywuzzy', 'groclient', 'numpy', 'pandas']

setup_kwargs = {
    'name': 'groclimateclient',
    'version': '1.0.0',
    'description': "Python client library for accessing Gro Intelligence's climate data",
    'long_description': '<p align="center"><img width="20%" src="https://gro-images.s3.amazonaws.com/Gro-Logo-Emble-Blue-LARGE.svg"></p>\n<h1 align="center">Gro Climate API Client</h1>',
    'author': 'Gro Intelligence developers',
    'author_email': 'dev@gro-intelligence.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.gro-intelligence.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
