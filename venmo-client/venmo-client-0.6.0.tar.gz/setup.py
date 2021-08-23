# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['venmo_client', 'venmo_client.model']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'requests', 'rich>=10.7.0,<11.0.0']

entry_points = \
{'console_scripts': ['venmo = venmo_client.cli:cli']}

setup_kwargs = {
    'name': 'venmo-client',
    'version': '0.6.0',
    'description': '',
    'long_description': None,
    'author': 'Sharad Vikram',
    'author_email': 'sharad.vikram@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
