# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['research_utils', 'research_utils.sqlite', 'research_utils.torch']

package_data = \
{'': ['*']}

install_requires = \
['pytorch-lightning>=1.2.2,<2.0.0',
 'sqlite-utils>=3.6,<4.0',
 'torch>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'research-utils',
    'version': '2021.8.21.4',
    'description': 'some utils for my research',
    'long_description': None,
    'author': 'Rainforest Cheng',
    'author_email': 'r08521610@ntu.edu.tw',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
