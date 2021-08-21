# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dobato']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dobato',
    'version': '1.0.0',
    'description': 'Simple tool for discord BOT',
    'long_description': None,
    'author': 'himkt',
    'author_email': 'himkt@klis.tsukuba.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
