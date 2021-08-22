# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grapdb', 'grapdb.target', 'grapdb.target.rsrc']

package_data = \
{'': ['*']}

install_requires = \
['code-writer>=1.1.1,<2.0.0', 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['grapdb = grapdb.cli:main']}

setup_kwargs = {
    'name': 'grapdb',
    'version': '0.6',
    'description': 'Graph data modeling and code generator for Postgres.',
    'long_description': None,
    'author': 'Ken Elkabany',
    'author_email': 'ken@elkabany.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
