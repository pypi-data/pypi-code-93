# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grepy']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['chuy = grepy:main']}

setup_kwargs = {
    'name': 'grepy',
    'version': '0.1.0',
    'description': 'A Grep clone',
    'long_description': '# Grepy\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/grep',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
