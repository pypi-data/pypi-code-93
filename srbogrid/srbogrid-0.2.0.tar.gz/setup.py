# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['srbogrid']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'numpy>=1.21.1,<2.0.0', 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'srbogrid',
    'version': '0.2.0',
    'description': 'Package for calculating space-reduced bond-order grids for diatomics',
    'long_description': None,
    'author': 'Lukasz Mentel',
    'author_email': 'lmmentel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
