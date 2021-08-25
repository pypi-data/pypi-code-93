# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['launcherp']

package_data = \
{'': ['*'], 'launcherp': ['assets/*']}

install_requires = \
['Kivy>=2.0.0,<3.0.0', 'Morpion>=0.3.4,<0.4.0']

setup_kwargs = {
    'name': 'launcherp',
    'version': '0.1.2',
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
