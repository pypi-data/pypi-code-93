# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beespammer']

package_data = \
{'': ['*']}

install_requires = \
['PyAutoGUI>=0.9.53,<0.10.0']

entry_points = \
{'console_scripts': ['beespammer = beespammer:main']}

setup_kwargs = {
    'name': 'beespammer',
    'version': '4.0.0',
    'description': 'Spam Text',
    'long_description': None,
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
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
