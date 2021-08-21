# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cay']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['cay = cay.cli:main']}

setup_kwargs = {
    'name': 'cay',
    'version': '0.1.2',
    'description': 'Simple calculator implemented in Python',
    'long_description': None,
    'author': 'Naoya Yamashita',
    'author_email': 'conao3@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/conao3/cay',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
