# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyshmht3']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyshmht3',
    'version': '0.1.1',
    'description': 'python share memory dict for py3',
    'long_description': None,
    'author': 'muyakongali',
    'author_email': 'muyakongali@tencent.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
