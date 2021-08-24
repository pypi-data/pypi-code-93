# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fate_test', 'fate_test.flow_test', 'fate_test.scripts']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'colorama>=0.4.4,<0.5.0',
 'fate_client==1.6.0',
 'loguru>=0.5.1,<0.6.0',
 'pandas>=1.1.5',
 'prettytable>=1.0.0,<2.0.0',
 'requests>=2.24.0,<3.0.0',
 'requests_toolbelt>=0.9.1,<0.10.0',
 'ruamel.yaml>=0.16.10,<0.17.0',
 'sshtunnel>=0.1.5,<0.2.0']

entry_points = \
{'console_scripts': ['fate_test = fate_test.scripts.cli:cli']}

setup_kwargs = {
    'name': 'fate-test',
    'version': '1.6.0',
    'description': 'test tools for FATE',
    'long_description': '# fate test\n',
    'author': 'FederatedAI',
    'author_email': 'contact@FedAI.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://fate.fedai.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
