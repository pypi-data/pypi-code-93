# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['partx']

package_data = \
{'': ['*']}

install_requires = \
['bokeh>=2.3.2,<3.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'pathos>=0.2.8,<0.3.0',
 'psy-taliro>=1.0.0a4,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.6.3,<2.0.0']

setup_kwargs = {
    'name': 'partx',
    'version': '0.1.2',
    'description': 'PartX Optimizer to use with PSY-Taliro',
    'long_description': None,
    'author': 'Aniruddh Chandratre',
    'author_email': 'achand75@asu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
