# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['guillotina_localstorage', 'guillotina_localstorage.tests']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0', 'guillotina>5.3.48']

setup_kwargs = {
    'name': 'guillotina-localstorage',
    'version': '0.2.0',
    'description': 'Local FS storage support for Guillotina',
    'long_description': '# guillotina_localstorage\n\n[![Build Status](https://travis-ci.org/vinissimus/guillotina_localstorage.svg?branch=master)](https://travis-ci.org/vinissimus/guillotina_localstorage) [![PyPI version](https://badge.fury.io/py/guillotina-localstorage.svg)](https://badge.fury.io/py/guillotina-localstorage) [![Codcov](https://codecov.io/gh/vinissimus/guillotina_localstorage/branch/master/graph/badge.svg)](https://codecov.io/gh/vinissimus/guillotina_localstorage/branch/master) ![](https://img.shields.io/pypi/pyversions/guillotina_localstorage.svg)\n\nLocal FS storage support for Guillotina.\n\n## Example\n\nExample config.json entry:\n\n```json\n{\n    "applications": [\n        "...",\n        "guillotina_localstorage"\n    ],\n    "storage": {"upload_folder": "/tmp"}\n}\n```\n\nThis library uses [aiofiles](https://github.com/Tinche/aiofiles)\n',
    'author': 'Jordi Masip',
    'author_email': 'jordi@masip.cat',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
