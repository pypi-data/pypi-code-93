# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tower_defense']

package_data = \
{'': ['*'], 'tower_defense': ['resources/*']}

install_requires = \
['pygame>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['clear-tower-defense-savefile = tower_defense.main:reset',
                     'tower-defense = tower_defense.main:app']}

setup_kwargs = {
    'name': 'tower-defense',
    'version': '2.4.7',
    'description': '',
    'long_description': None,
    'author': 'Ying Liqian',
    'author_email': 'jamesylq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
