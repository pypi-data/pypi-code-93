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
    'version': '0.1.2',
    'description': 'Lightning Network BOLT12 Routines',
    'long_description': '# Lightning Network BOLT12 Routines\n\nThis is a simple Python 3 library to read, check, generate and\nmanipulate [BOLT 12](https://bolt12.org) offers, invoice_requests and\ninvoices.\n\nSee [examples/](examples/) for usage.\n',
    'author': 'Rusty Russell',
    'author_email': 'rusty@rustcorp.com.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rustyrussell/bolt12/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
