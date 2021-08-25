# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tisane', 'tisane.gui', 'tisane.smt']

package_data = \
{'': ['*'], 'tisane.gui': ['example_inputs/*']}

install_requires = \
['Flask>=1.1.2,<2.0.0',
 'coverage>=5.5,<6.0',
 'dash-bootstrap-components>=0.12.0,<0.13.0',
 'dash-daq>=0.5.0,<0.6.0',
 'dash>=1.20.0,<2.0.0',
 'h5>=0.4.1,<0.5.0',
 'h5py>=3.3.0,<4.0.0',
 'more-itertools>=8.7.0,<9.0.0',
 'networkx>=2.5.1,<3.0.0',
 'pandas>=1.1.0,<2.0.0',
 'patsy>=0.5.1,<0.6.0',
 'plotly>=4.14.3,<5.0.0',
 'pydot>=1.4.2,<2.0.0',
 'pymer4>=0.7.5,<0.8.0',
 'pytest-cov>=2.11.1,<3.0.0',
 'pytest>=6.2.4,<7.0.0',
 'statsmodels>=0.12.2,<0.13.0',
 'tweedie>=0.0.7,<0.0.8']

setup_kwargs = {
    'name': 'tisane',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Eunice Jun',
    'author_email': 'eunice.m.jun@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.11,<4.0.0',
}


setup(**setup_kwargs)
