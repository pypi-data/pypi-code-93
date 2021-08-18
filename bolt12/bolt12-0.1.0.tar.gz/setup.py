# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bolt12']

package_data = \
{'': ['*']}

install_requires = \
['bech32>=1.2.0,<2.0.0',
 'pyln-proto>=0.10.1,<0.11.0',
 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'bolt12',
    'version': '0.1.0',
    'description': 'Lightning Network BOLT12 Routines',
    'long_description': None,
    'author': 'Rusty Russell',
    'author_email': 'rusty@rustcorp.com.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
