# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crossapp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'crossapp',
    'version': '0.1.0',
    'description': 'A zipapp based app packaging and distribution utility for Python.',
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
