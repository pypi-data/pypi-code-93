# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paloalto_xapi_wrapper']

package_data = \
{'': ['*']}

install_requires = \
['paloalto-env', 'pan-python>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'paloalto-xapi-wrapper',
    'version': '0.1.3',
    'description': 'Xapi wrapper for quick use',
    'long_description': None,
    'author': 'Thomas Christory',
    'author_email': 'thomas@christory.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
