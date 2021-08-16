# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wiki_cli']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'lxml>=4.6.2,<5.0.0',
 'pre-commit>=2.9.3,<3.0.0',
 'pyfzf>=0.2.2,<0.3.0',
 'requests>=2.25.0,<3.0.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['wiki = wiki_cli.wiki:main']}

setup_kwargs = {
    'name': 'wiki-cli',
    'version': '0.4.0',
    'description': 'Command Line Client for quick lookups on Wikipedia.',
    'long_description': None,
    'author': 'sedrubal',
    'author_email': 'dev@sedrubal.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/sedrubal/wiki-cli.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
