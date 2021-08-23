# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipecheck', 'pipecheck.checks']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'certifi>=2021.5.30,<2022.0.0',
 'icecream>=2.1.0,<3.0.0',
 'icmplib>=3.0,<4.0',
 'netaddr>=0.8.0,<0.9.0',
 'prometheus-client>=0.11.0,<0.12.0',
 'termcolor>=1.1.0,<2.0.0',
 'urllib3>=1.26.5,<2.0.0']

setup_kwargs = {
    'name': 'pipecheck',
    'version': '0.2.3',
    'description': "This simple tool can be used to verify the state of a system's context.",
    'long_description': None,
    'author': 'Michael Riedmann',
    'author_email': 'michael_riedmann@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
