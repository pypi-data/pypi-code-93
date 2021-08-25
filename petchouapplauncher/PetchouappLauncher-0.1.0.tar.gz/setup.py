# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['petchouapplauncher']

package_data = \
{'': ['*'], 'petchouapplauncher': ['assets/*']}

install_requires = \
['Kivy>=2.0.0,<3.0.0', 'morpion>=0.3.3,<0.4.0']

setup_kwargs = {
    'name': 'petchouapplauncher',
    'version': '0.1.0',
    'description': 'A nice way to launch my other projects',
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
