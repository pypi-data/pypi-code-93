# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proman_common']

package_data = \
{'': ['*']}

install_requires = \
['compendium[toml]>=0.1.1-alpha.0,<0.2.0', 'keyring>=23.0.1,<24.0.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.8,<0.9'],
 'gnome:sys_platform == "linux"': ['SecretStorage>=3.3.1,<4.0.0'],
 'kde:sys_platform == "linux"': ['dbus-python>=1.2.16,<2.0.0']}

setup_kwargs = {
    'name': 'proman-common',
    'version': '0.1.1a1',
    'description': 'GitHub based package manager.',
    'long_description': None,
    'author': 'Jesse P. Johnson',
    'author_email': 'jpj6652@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
