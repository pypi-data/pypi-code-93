# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ospyata']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ospyata',
    'version': '1.0.2',
    'description': 'Python bindings for osmata.',
    'long_description': None,
    'author': 'aerocyber',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
