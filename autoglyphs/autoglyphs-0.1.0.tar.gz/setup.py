# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autoglyphs']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'web3>=5.23.0,<6.0.0']

setup_kwargs = {
    'name': 'autoglyphs',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'j1c',
    'author_email': 'jaewonc78@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
