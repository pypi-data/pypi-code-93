# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vgsstyle', 'vgsstyle.linters']

package_data = \
{'': ['*']}

install_requires = \
['black>=20.8b1,<21.0',
 'click>6,<9',
 'flake8-import-order>=0.18.1,<0.19.0',
 'flake8>=3.8.4,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['vgs-style = vgsstyle.cli:main']}

setup_kwargs = {
    'name': 'vgs-style',
    'version': '1.0.3',
    'description': 'Library for linting and formatting Python source code',
    'long_description': None,
    'author': 'Petro Melnykov',
    'author_email': 'petro.melnykov@vgs.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4',
}


setup(**setup_kwargs)
