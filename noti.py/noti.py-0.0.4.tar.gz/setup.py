# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noti_py']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'click>=8.0.1,<9.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'noti.py',
    'version': '0.0.4',
    'description': 'Simple, Python-based notification script to post a message to a materix server via the Matrix client/server API',
    'long_description': None,
    'author': 'Alex Kelly',
    'author_email': 'kellya@arachnitech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
