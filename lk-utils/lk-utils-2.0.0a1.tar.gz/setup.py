# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lk_utils', 'lk_utils.resource.metadata', 'lk_utils.typehint']

package_data = \
{'': ['*'], 'lk_utils': ['resource/*', 'resource/metadata/more/*']}

install_requires = \
['lk-logger', 'xlrd==1.2', 'xlsxwriter']

setup_kwargs = {
    'name': 'lk-utils',
    'version': '2.0.0a1',
    'description': 'LK Utils is made for data processing.',
    'long_description': None,
    'author': 'Likianta',
    'author_email': 'likianta@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
