# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paperpile_notion']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'emojis>=0.6.0,<0.7.0',
 'notion-database>=20210513.7,<20210514.0',
 'notion>=0.0.28,<0.0.29',
 'pandas>=1.3.2,<2.0.0',
 'ruamel.yaml>=0.17.13,<0.18.0',
 'tqdm>=4.62.1,<5.0.0']

entry_points = \
{'console_scripts': ['paperpile-notion = paperpile_notion.commands:cli']}

setup_kwargs = {
    'name': 'paperpile-notion',
    'version': '0.1.0',
    'description': 'Sync Notion with Paperpile',
    'long_description': None,
    'author': 'John M',
    'author_email': '5000729+jmuchovej@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
