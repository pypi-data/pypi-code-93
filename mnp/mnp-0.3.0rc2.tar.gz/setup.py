# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mnp']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-tools>=1.37.1,<2.0.0',
 'grpcio>=1.37.1,<2.0.0',
 'protobuf>=3.16.0,<4.0.0']

setup_kwargs = {
    'name': 'mnp',
    'version': '0.3.0rc2',
    'description': '',
    'long_description': None,
    'author': 'Mantik Team',
    'author_email': 'info@mantik.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.mantik.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.8',
}


setup(**setup_kwargs)
