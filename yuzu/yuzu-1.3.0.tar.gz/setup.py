# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yuzu']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'yuzu',
    'version': '1.3.0',
    'description': 'Lightweight and useful annotation package for logging and caching',
    'long_description': '==============\nyuzu\n==============\n\n\n.. image:: https://img.shields.io/pypi/v/yuzu.svg\n        :target: https://pypi.python.org/pypi/yuzu\n\n.. image:: https://readthedocs.org/projects/yuzu-python/badge/?version=latest\n        :target: https://yuzu-python.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n\n\n\nLightweight and useful annotation package for logging and caching\n\n\n* Free software: MIT license\n* Documentation: https://yuzu-python.readthedocs.io.\n\n\nFeatures\n--------\n\n* TODO\n\n  - write document\n\nCredits\n-------\n',
    'author': 'Yasunori Horikoshi',
    'author_email': 'hotoku@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hotoku/yuzu',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
