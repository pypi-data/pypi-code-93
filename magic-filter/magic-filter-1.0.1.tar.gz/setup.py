# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magic_filter', 'magic_filter.operations']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'magic-filter',
    'version': '1.0.1',
    'description': 'This package provides magic filter based on dynamic attribute getter',
    'long_description': '# magic-filter\n\nThis package provides magic filter based on dynamic attribute getter\n',
    'author': 'Alex Root Junior',
    'author_email': 'pypi@aiogram.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aiogram/magic-filter/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
