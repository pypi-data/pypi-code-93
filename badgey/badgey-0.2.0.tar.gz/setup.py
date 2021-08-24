# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['badgey']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.20,<4.0.0',
 'docopt>=0.6.2,<0.7.0',
 'matplotlib>=3.4.3,<4.0.0',
 'pybadges>=2.2.1,<3.0.0']

entry_points = \
{'console_scripts': ['badgey = badgey:main']}

setup_kwargs = {
    'name': 'badgey',
    'version': '0.2.0',
    'description': 'A library and a CLI to locally generate project badges',
    'long_description': None,
    'author': 'Ruben Di Battista',
    'author_email': 'rubendibattista@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
