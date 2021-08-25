# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['n_edit']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5>=5.15.4,<6.0.0', 'click>=8.0.1,<9.0.0']

setup_kwargs = {
    'name': 'n-edit',
    'version': '0.3.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
