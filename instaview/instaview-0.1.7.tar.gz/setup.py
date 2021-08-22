# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['instaview']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2', 'fire>=0.4.0,<0.5.0', 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['instaview = instaview.cli:cli']}

setup_kwargs = {
    'name': 'instaview',
    'version': '0.1.7',
    'description': 'this package is just a scrapper of insta-stories.online',
    'long_description': None,
    'author': 'nowhere man',
    'author_email': 'man@nowhere.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
