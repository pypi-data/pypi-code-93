# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kwork', 'kwork.types']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0', 'pydantic>=1.4,<2.0', 'websockets>=8.1,<9.0']

setup_kwargs = {
    'name': 'kwork',
    'version': '0.0.5',
    'description': 'simple async wrapper for kwork.ru',
    'long_description': None,
    'author': 'kesha1225',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
