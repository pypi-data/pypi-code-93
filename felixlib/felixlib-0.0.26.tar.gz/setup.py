# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['felixlib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'felixlib',
    'version': '0.0.26',
    'description': 'felixlib',
    'long_description': None,
    'author': 'spectereye',
    'author_email': 'spectereye@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
}


setup(**setup_kwargs)
