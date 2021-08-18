# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streetcrawl']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.1,<9.0.0',
 'click>=8.0.1,<9.0.0',
 'geopy>=2.2.0,<3.0.0',
 'loguru>=0.5.3,<0.6.0',
 'methodtools>=0.4.5,<0.5.0',
 'pytest-cov>=2.12.1,<3.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'streetcrawl',
    'version': '0.1.0',
    'description': 'Google Streetview panoramas collector',
    'long_description': None,
    'author': 'monomonedula',
    'author_email': 'valh@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
