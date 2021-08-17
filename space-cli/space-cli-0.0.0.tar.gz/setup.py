# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['space_cli']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'space-cli',
    'version': '0.0.0',
    'description': 'XYZ',
    'long_description': None,
    'author': 'Abbas Jafari',
    'author_email': 'abbas.jafari@powercoders.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
