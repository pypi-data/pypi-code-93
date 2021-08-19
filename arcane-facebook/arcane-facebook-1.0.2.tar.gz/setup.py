# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcane', 'arcane.facebook']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.10.0,<2.0.0',
 'facebook_business==11.0.0',
 'typing-extensions>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'arcane-facebook',
    'version': '1.0.2',
    'description': 'Helpers to request facebook API',
    'long_description': '# Arcane facebook\n',
    'author': 'Arcane',
    'author_email': 'product@arcane.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
