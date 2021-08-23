# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['archivr']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'tqdm>=4.62.2,<5.0.0']

setup_kwargs = {
    'name': 'archivr',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Sam Wilson',
    'author_email': 'skwilson3@crimson.ua.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
