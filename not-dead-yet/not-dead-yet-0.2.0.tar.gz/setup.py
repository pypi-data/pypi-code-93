# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['not_dead_yet']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['ndy = not_dead_yet.__main__:main']}

setup_kwargs = {
    'name': 'not-dead-yet',
    'version': '0.2.0',
    'description': 'A simple live server implementation.',
    'long_description': None,
    'author': 'Angus Hollands',
    'author_email': 'goosey15@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
