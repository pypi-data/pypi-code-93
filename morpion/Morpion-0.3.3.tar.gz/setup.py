# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['Morpion']

package_data = \
{'': ['*']}

install_requires = \
['art>=5.2,<6.0', 'termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'morpion',
    'version': '0.3.3',
    'description': 'A nice Morpion game',
    'long_description': None,
    'author': 'PetchouHelper',
    'author_email': 'petchou91d@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
