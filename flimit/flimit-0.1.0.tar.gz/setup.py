# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flimit']

package_data = \
{'': ['*']}

install_requires = \
['psutil>=5.8.0,<6.0.0']

setup_kwargs = {
    'name': 'flimit',
    'version': '0.1.0',
    'description': 'Limit time and memory usage from a function',
    'long_description': None,
    'author': 'Quentin Fortier',
    'author_email': 'qpfortier@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
