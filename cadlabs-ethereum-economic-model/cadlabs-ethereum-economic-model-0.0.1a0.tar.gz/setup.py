# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['model', 'model.parts', 'model.parts.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cadlabs-ethereum-economic-model',
    'version': '0.0.1a0',
    'description': '',
    'long_description': None,
    'author': 'BenSchZA',
    'author_email': 'BenSchZA@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
