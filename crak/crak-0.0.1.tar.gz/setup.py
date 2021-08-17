# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crak']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0', 'pandas>=1.3.2,<2.0.0', 'passlib>=1.7.4,<2.0.0']

entry_points = \
{'console_scripts': ['crak = crak.cli:main']}

setup_kwargs = {
    'name': 'crak',
    'version': '0.0.1',
    'description': 'Bruteforce password cracker',
    'long_description': None,
    'author': 'Stephen Eaton',
    'author_email': 'seaton@strobotics.com.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
