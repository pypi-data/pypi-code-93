# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gerald_tools', 'gerald_tools.utils']

package_data = \
{'': ['*']}

install_requires = \
['ImageHash>=4.2.1,<5.0.0',
 'aenum>=3.1.0,<4.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.2,<2.0.0',
 'opencv-python>=4.5.3,<5.0.0',
 'pytest>=6.2.4,<7.0.0',
 'torch>=1.9.0,<2.0.0',
 'torchvision>=0.10.0,<0.11.0',
 'tqdm>=4.62.2,<5.0.0']

setup_kwargs = {
    'name': 'gerald-tools',
    'version': '0.1.0',
    'description': 'Tools for importings the GERALD Dataset',
    'long_description': None,
    'author': 'Philipp Simon Leibner',
    'author_email': 'philipp.leibner@ifs.rwth-aachen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
