# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pfhedge',
 'pfhedge._utils',
 'pfhedge.features',
 'pfhedge.instruments',
 'pfhedge.instruments.derivative',
 'pfhedge.instruments.primary',
 'pfhedge.nn',
 'pfhedge.nn.modules',
 'pfhedge.nn.modules.bs',
 'pfhedge.stochastic']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.9.0,<2.0.0', 'tqdm>=4.59.0,<5.0.0']

setup_kwargs = {
    'name': 'pfhedge',
    'version': '0.10.4',
    'description': 'Deep Hedging in PyTorch',
    'long_description': None,
    'author': 'Shota Imaki',
    'author_email': 'shota.imaki.0801@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pfnet-research/pfhedge',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.13,<4.0.0',
}


setup(**setup_kwargs)
