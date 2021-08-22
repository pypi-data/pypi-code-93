# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['puck_me', 'puck_me.lib', 'puck_me.skater']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'html5lib>=1.1,<2.0',
 'lxml>=4.6.3,<5.0.0',
 'pandas>=1.3.1,<2.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'puck-me',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Nathan',
    'author_email': 'nathansaccon10@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
