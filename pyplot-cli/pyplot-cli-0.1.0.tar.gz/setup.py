# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyplot_cli']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3.9.2,<4.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.3.1,<2.0.0',
 'typer>=0.3.2,<0.4.0',
 'yapf>=0.31.0,<0.32.0']

entry_points = \
{'console_scripts': ['pyplt = pyplot_cli.cli:run']}

setup_kwargs = {
    'name': 'pyplot-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Minjoon Hong',
    'author_email': 'mjhong0708@yonsei.ac.kr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
