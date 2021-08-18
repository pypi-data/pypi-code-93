# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bunnyapi']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'bunnyapi',
    'version': '0.1.1',
    'description': 'bunny.net API client',
    'long_description': None,
    'author': "Andy 'danjo' Jacobsen",
    'author_email': 'atze.danjo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
