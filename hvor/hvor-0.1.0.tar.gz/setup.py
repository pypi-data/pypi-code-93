# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hvor']

package_data = \
{'': ['*'], 'hvor': ['resources/*']}

install_requires = \
['Rtree>=0.9.7,<0.10.0',
 'geopandas>=0.9.0,<0.10.0',
 'setuptools>=57.4.0,<58.0.0']

setup_kwargs = {
    'name': 'hvor',
    'version': '0.1.0',
    'description': 'A library for assigning Norwegian metadata to coordinates',
    'long_description': None,
    'author': 'Espen Hafstad Solvang',
    'author_email': 'espenhafstadsolvang@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
