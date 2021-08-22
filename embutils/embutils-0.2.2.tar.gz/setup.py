# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['embutils',
 'embutils.repo',
 'embutils.serial',
 'embutils.serial.core',
 'embutils.serial.data',
 'embutils.utils']

package_data = \
{'': ['*']}

install_requires = \
['intelhex>=2.3.0,<3.0.0', 'pyserial>=3.5,<4.0']

entry_points = \
{'console_scripts': ['cover = scripts.poetry:run_coverage',
                     'docs = scripts.poetry:run_docs',
                     'html = scripts.poetry:run_html',
                     'linter = scripts.poetry:run_linter',
                     'test = scripts.poetry:run_test',
                     'version = scripts.poetry:run_version']}

setup_kwargs = {
    'name': 'embutils',
    'version': '0.2.2',
    'description': 'Python utilities for embedded projects',
    'long_description': '# Embutils \n[![PyPI version](https://badge.fury.io/py/embutils.svg)](https://badge.fury.io/py/embutils)\n[![Docs Status](https://readthedocs.org/projects/embutils/badge/?version=latest)](https://embutils.readthedocs.io/en/latest/?badge=latest)\n[![License](https://img.shields.io/:license-mit-blue.svg?style=flat-square)](https://badges.mit-license.org)\n\nPython utilities for embedded projects. \n\n## Installation \nYou can get the packaged version from [PyPI](https://pypi.org/project/embutils/):\n```\npip install embutils\n```',
    'author': 'Christian Wiche',
    'author_email': 'cwichel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cwichel/embutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
