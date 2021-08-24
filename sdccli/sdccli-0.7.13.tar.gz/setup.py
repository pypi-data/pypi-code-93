# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sdccli',
 'sdccli.cli',
 'sdccli.cli.dashboard',
 'sdccli.cli.formatter',
 'sdccli.cli.formatter.json_formatter',
 'sdccli.cli.formatter.text_formatter',
 'sdccli.cli.formatter.text_formatter.scanning',
 'sdccli.cli.policy',
 'sdccli.cli.scanning',
 'sdccli.cli.scanning.vulnerability',
 'sdccli.cli.settings',
 'sdccli.usecases',
 'sdccli.usecases.backup',
 'sdccli.usecases.dashboard',
 'sdccli.usecases.policy',
 'sdccli.usecases.scanning',
 'sdccli.usecases.settings']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'prettytable>=2,<3',
 'python-dateutil>=2.8.1,<3.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'requests>=2,<3',
 'sdcclient>=0.16.1,<0.17.0']

entry_points = \
{'console_scripts': ['sdc-cli = sdccli.cli:cli']}

setup_kwargs = {
    'name': 'sdccli',
    'version': '0.7.13',
    'description': 'CLI client for Sysdig Cloud',
    'long_description': None,
    'author': 'Sysdig Inc.',
    'author_email': 'info@sysdig.com',
    'maintainer': 'Nestor Salceda',
    'maintainer_email': 'nestor.salceda@sysdig.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
