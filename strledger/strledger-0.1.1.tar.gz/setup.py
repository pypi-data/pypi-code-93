# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strledger']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'construct==2.10.61',
 'ledgerwallet>=0.1.2,<0.2.0',
 'stellar-sdk>=4.1.0,<5.0.0']

entry_points = \
{'console_scripts': ['strledger = strledger.cli:cli']}

setup_kwargs = {
    'name': 'strledger',
    'version': '0.1.1',
    'description': 'Sign Stellar Transaction with Ledger on the command line.',
    'long_description': '# strledger - Sign Stellar Transaction with Ledger on the command line.\n\n## Installation\n```shell\npip install -U strledger\n```\n\n## Usage\n```text\nUsage: strledger [OPTIONS] COMMAND [ARGS]...\n\n  Stellar Ledger commands.\n\n  This project is built on the basis of ledgerctl, you can check ledgerctl for more features.\n\nOptions:\n  -v, --verbose  Display exchanged APDU.\n  --help         Show this message and exit.\n\nCommands:\n  app-config   Get Stellar app config.\n  get-address  Get Stellar public address.\n  sign-tx      Sign a base64-encoded transaction envelope.\n  version      Get version info.\n```',
    'author': 'overcat',
    'author_email': '4catcode@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/overcat/strledger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
