# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ardkit']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['ardkit = ardkit.__main__:main']}

setup_kwargs = {
    'name': 'ardkit',
    'version': '1.1.0',
    'description': 'ardkit',
    'long_description': '# Ardkit\n',
    'author': 'Ardustri',
    'author_email': 'contact@ardkit.netlify.app',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ardustri/ardkit',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
