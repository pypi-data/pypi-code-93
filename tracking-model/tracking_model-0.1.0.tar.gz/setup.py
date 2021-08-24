# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tracking_model']

package_data = \
{'': ['*']}

install_requires = \
['cvxopt>=1.2.6,<2.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'tracking-model',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Adriel Martins',
    'author_email': 'adrielfalcao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
