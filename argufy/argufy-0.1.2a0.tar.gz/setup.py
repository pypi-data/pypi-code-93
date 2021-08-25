# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['argufy']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0', 'docstring-parser>=0.7.2,<0.8.0']

setup_kwargs = {
    'name': 'argufy',
    'version': '0.1.2a0',
    'description': 'Inspection based parser based on argparse.',
    'long_description': None,
    'author': 'Jesse P. Johnson',
    'author_email': 'jpj6652@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
