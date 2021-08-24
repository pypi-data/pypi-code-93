# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mypo',
 'mypo.evacuator',
 'mypo.optimizer',
 'mypo.rebalancer',
 'mypo.reporter',
 'mypo.sampler',
 'mypo.trigger']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.0.1,<2.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pandas>=1.2.2,<2.0.0',
 'pymc3>=3.11.1,<4.0.0',
 'scipy>=1.6.0,<2.0.0',
 'tqdm>=4.59.0,<5.0.0',
 'yfinance>=0.1.62,<0.2.0']

setup_kwargs = {
    'name': 'mypo',
    'version': '0.0.85',
    'description': '',
    'long_description': "mypo is a Python module for making strategy your portfolio and is distributed under the MIT license.\n\nInstallation\n============\n\nYou can install the latest this module with the command:\n\n\n    pip install mypo\n\nQuick start\n============\n\nYou can start quickly  by using docker image with the command.\n\n\n    git clone https://github.com/sonesuke/mypo.git\n    docker-compose up\n\nAfter starting Jupyter server, you can login it with the token. The default of token is '1111'.\n\n\nImportant links\n===============\n\n- Documentation: https://sonesuke.github.io/mypo\n- Official source code repo: https://github.com/sonesuke/mypo\n- Download releases: https://pypi.org/project/mypo/\n- Issue tracker: https://github.com/sonesuke/mypo/issues\n\nCitation\n========\nIf you use mypo in a publication, we would appreciate citations: https://sonesuke.github.io/mypo/",
    'author': 'sonesuke',
    'author_email': 'iamsonesuke@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sonesuke/mypo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.10,<4.0.0',
}


setup(**setup_kwargs)
