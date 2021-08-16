# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.pinterest']

package_data = \
{'': ['*']}

install_requires = \
['arcane-core>=1.2.8,<2.0.0',
 'backoff>=1.10.0,<2.0.0',
 'requests>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'arcane-pinterest',
    'version': '0.3.0',
    'description': 'Helpers to request Pinterest API ',
    'long_description': None,
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
