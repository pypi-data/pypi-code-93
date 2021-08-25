# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lgblkb_tools',
 'lgblkb_tools.common',
 'lgblkb_tools.db',
 'lgblkb_tools.geometry',
 'lgblkb_tools.geometry.utils']

package_data = \
{'': ['*']}

install_requires = \
['checksumdir',
 'colorlog',
 'dynaconf',
 'geoalchemy2',
 'geojson',
 'geopandas',
 'invoke',
 'matplotlib',
 'more-itertools',
 'networkx',
 'numpy',
 'opencv-python',
 'ortools',
 'pandas',
 'pyproj',
 'python-box[ruamel.yaml,toml]',
 'python-log-indenter',
 'python-telegram-bot',
 'pyyaml',
 'requests',
 'scikit-learn',
 'scipy',
 'shapely',
 'sortedcontainers',
 'sqlalchemy',
 'ujson>=4.1.0,<5.0.0',
 'visilibity',
 'wrapt']

setup_kwargs = {
    'name': 'lgblkb-tools',
    'version': '2.1.0',
    'description': 'Helper tools for lgblkb)',
    'long_description': None,
    'author': 'lgblkb',
    'author_email': 'dbakhtiyarov@nu.edu.kz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
