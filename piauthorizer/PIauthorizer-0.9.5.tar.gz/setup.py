# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['piauthorizer',
 'piauthorizer.ConfigManager',
 'piauthorizer.autorest',
 'piauthorizer.functional',
 'piauthorizer.logging']

package_data = \
{'': ['*'],
 'piauthorizer.ConfigManager': ['credential_templates/*', 'logging/*']}

install_requires = \
['PyJWT>=2.0.1,<3.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'cryptography>=3.4.7,<4.0.0',
 'fastapi>=0.62.0',
 'python-multipart>=0.0.5,<0.0.6']

setup_kwargs = {
    'name': 'piauthorizer',
    'version': '0.9.5',
    'description': 'A package to create a uniform authorization and autorest standard for FastAPI. Along with integration with out Application Configuration server.',
    'long_description': None,
    'author': 'David Berenstein',
    'author_email': 'david.berenstein@pandoraintelligence.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
