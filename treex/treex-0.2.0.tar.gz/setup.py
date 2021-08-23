# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['treex', 'treex.nn']

package_data = \
{'': ['*']}

install_requires = \
['flax>=0.3.4,<0.4.0', 'jax>=0.2.18,<0.3.0', 'jaxlib>=0.1.70,<0.2.0']

setup_kwargs = {
    'name': 'treex',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Cristian Garcia',
    'author_email': 'cgarcia.e88@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
