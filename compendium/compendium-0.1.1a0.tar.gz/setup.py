# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['compendium', 'compendium.filetypes']

package_data = \
{'': ['*']}

install_requires = \
['anytree>=2.8.0,<3.0.0',
 'dpath>=2.0.1,<3.0.0',
 'ruamel.yaml>=0.16.10,<0.17.0',
 'tomlkit>=0.7.0,<0.8.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.8,<0.9'],
 'xml': ['xmltodict>=0.12.0,<0.13.0']}

setup_kwargs = {
    'name': 'compendium',
    'version': '0.1.1a0',
    'description': 'Simple layered configuraion tool',
    'long_description': "# Compendium\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![Build Status](https://travis-ci.org/kuwv/python-compendium.svg?branch=master)](https://travis-ci.org/kuwv/python-compendium)\n[![codecov](https://codecov.io/gh/kuwv/python-compendium/branch/master/graph/badge.svg)](https://codecov.io/gh/kuwv/python-compendium)\n\n## Overview\n\nCompendium is a simple configuration management tool. It has the capability to manage configuration files writen in JSON, TOML, XML and YAML. Settings from these configuration files can then be managed easily with the help of dpath.\n\n## Documentation\n\nhttps://kuwv.github.io/python-compendium/\n\n## Install\n\n`pip install compendium`\n\n## Manage configuration\n\n```\nfrom compendium.config_manager import ConfigManager\n\ncfg = ConfigManager(application='app', path='afile.toml')\ncfg.load()\n```\n\n## Search settings\n\n`query = cfg.search('/servers/**/ip')`\n\n## Create settings\n\n`cfg.create('/test', 'test')`\n\n## Update settings\n\n`cfg.set('/owner/name', 'Tom Waits')`\n\n## Delete settings\n\n`cfg.delete('/owner/name')`\n",
    'author': 'Jesse P. Johnson',
    'author_email': 'jpj6652@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
