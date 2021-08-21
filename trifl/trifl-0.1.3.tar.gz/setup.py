# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trifl', 'trifl.filters', 'trifl.parse']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'biopython>=1.78,<2.0',
 'click>=8.0.1,<9.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'peewee>=3.14.4,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'scipy>=1.6.3,<2.0.0']

setup_kwargs = {
    'name': 'trifl',
    'version': '0.1.3',
    'description': 'TRIFL is a data filtration library for MS-proteomics experiments.',
    'long_description': None,
    'author': 'Radu Suciu',
    'author_email': 'radusuciu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
