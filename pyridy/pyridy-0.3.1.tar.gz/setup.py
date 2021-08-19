# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyridy', 'pyridy.osm', 'pyridy.osm.utils', 'pyridy.utils']

package_data = \
{'': ['*']}

install_requires = \
['geopy>=2.1.0,<3.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'numpy>=1.20.2,<2.0.0',
 'overpy>=0.6,<0.7',
 'pandas>=1.2.4,<2.0.0',
 'pyproj>=3.0.1,<4.0.0',
 'pytest>=6.2.3,<7.0.0',
 'requests>=2.25.1,<3.0.0',
 'scipy>=1.6.3,<2.0.0',
 'tqdm>=4.60.0,<5.0.0']

setup_kwargs = {
    'name': 'pyridy',
    'version': '0.3.1',
    'description': 'Support library for measurements made with the Ridy Android App',
    'long_description': '# PyRidy\n\nPython Support Library to import and process Ridy files\n\n# Installation\n\nInstall using pip, i.e. "pip install pyridy"\n',
    'author': 'Philipp Simon Leibner',
    'author_email': 'philipp.leibner@ifs.rwth-aachen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
