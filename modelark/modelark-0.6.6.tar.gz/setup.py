# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modelark',
 'modelark.common',
 'modelark.connector',
 'modelark.filterer',
 'modelark.repository']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'modelark',
    'version': '0.6.6',
    'description': 'Models Definition and Management Library',
    'long_description': None,
    'author': 'Knowark',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
