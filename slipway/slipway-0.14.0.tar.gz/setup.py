# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slipway', 'slipway.client', 'slipway.xdg_open']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3,<6.0', 'docker>=4.0.0,<5.0.0']

entry_points = \
{'console_scripts': ['slipway = slipway:main']}

setup_kwargs = {
    'name': 'slipway',
    'version': '0.14.0',
    'description': 'CLI tool for managing development containers',
    'long_description': None,
    'author': 'AGhost-7',
    'author_email': 'jonathan.boudreau.92@gmail.com',
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
