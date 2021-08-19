# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nbox']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nbox',
    'version': '0.1.3',
    'description': 'Makes using a host of opensource deep learning algorithms easier',
    'long_description': None,
    'author': 'Yash Bonde',
    'author_email': 'bonde.yash97@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
