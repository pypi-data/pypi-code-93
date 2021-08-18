# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ospyata']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodome>=3.10.1,<4.0.0',
 'requests>=2.26.0,<3.0.0',
 'shortlink>=0.1.6,<0.2.0']

setup_kwargs = {
    'name': 'ospyata',
    'version': '1.0.0',
    'description': 'Python bindings for osmata.',
    'long_description': None,
    'author': 'aerocyber',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
