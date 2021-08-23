# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tsdoc0', 'tsdoc0.python']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.3.0,<21.0.0', 'textx_ls_core>=0.1.1,<0.2.0']

entry_points = \
{'textx_languages': ['tsdoc0.python = tsdoc0.python:register']}

setup_kwargs = {
    'name': 'tsdoc0',
    'version': '0.30.0',
    'description': 'TSDoc is an embedded comment language for TechSmart code files.',
    'long_description': None,
    'author': 'Ryan Sobol',
    'author_email': 'ryan.sobol@techsmart.codes',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/techsmartkids/tsedu',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
