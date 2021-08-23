# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yaml_patch']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'ruamel.yaml>=0.17.11,<0.18.0']

setup_kwargs = {
    'name': 'yaml-patch',
    'version': '0.1.0',
    'description': 'Patch yaml strings',
    'long_description': None,
    'author': 'Diogo de Campos',
    'author_email': 'campos.ddc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
