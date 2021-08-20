# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['absorb',
 'absorb.config',
 'absorb.core',
 'absorb.core.idea',
 'absorb.core.kanban',
 'absorb.core.tasks',
 'absorb.utils']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.17,<4.0.0',
 'Pygments>=2.9.0,<3.0.0',
 'click-plugins>=1.1.1,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'commonmark>=0.9.1,<0.10.0',
 'gitdb>=4.0.7,<5.0.0',
 'importlib-metadata>=4.5.0,<5.0.0',
 'python-json-logger>=2.0.1,<3.0.0',
 'rich>=10.3.0,<11.0.0',
 'smmap>=4.0.0,<5.0.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'zipp>=3.4.1,<4.0.0']

entry_points = \
{'console_scripts': ['absorb = absorb.main:cli']}

setup_kwargs = {
    'name': 'absorb',
    'version': '0.1.1',
    'description': 'The extensible, feature-rich CLI workspace.',
    'long_description': None,
    'author': 'Aadhav Vignesh',
    'author_email': 'aadhav.n1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
