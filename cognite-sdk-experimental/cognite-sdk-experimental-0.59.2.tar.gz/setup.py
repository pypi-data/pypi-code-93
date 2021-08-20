# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite',
 'cognite.experimental',
 'cognite.experimental._api',
 'cognite.experimental._api.model_hosting',
 'cognite.experimental.data_classes',
 'cognite.experimental.data_classes.model_hosting',
 'cognite.experimental.data_classes.utils']

package_data = \
{'': ['*']}

install_requires = \
['cognite-sdk>=2.22,<3.0',
 'pandas>=1.1,<2.0',
 'regex>=2020.11.13,<2021.0.0',
 'responses>=0.13.3,<0.14.0',
 'sympy>=1.3.0,<2.0.0',
 'typing-extensions>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'cognite-sdk-experimental',
    'version': '0.59.2',
    'description': 'Experimental additions to the Python SDK',
    'long_description': None,
    'author': 'Sander Land',
    'author_email': 'sander.land@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
