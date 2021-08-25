# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['byteparsing']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0']

setup_kwargs = {
    'name': 'byteparsing',
    'version': '0.1.1',
    'description': 'Parser for mixed ASCII/binary data formats',
    'long_description': None,
    'author': 'Johan Hidding',
    'author_email': 'j.hidding@esciencecenter.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
