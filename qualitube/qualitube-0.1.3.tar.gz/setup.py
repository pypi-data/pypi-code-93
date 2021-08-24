# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qualitube']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.4,<2.0.0', 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['qualitube = qualitube.main:main']}

setup_kwargs = {
    'name': 'qualitube',
    'version': '0.1.3',
    'description': 'A Python package for YouTube qualitative data analysis',
    'long_description': None,
    'author': 'Vitor Mussa',
    'author_email': 'vtrmussa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
