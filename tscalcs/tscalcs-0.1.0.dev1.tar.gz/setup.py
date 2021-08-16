# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tscalcs']

package_data = \
{'': ['*']}

install_requires = \
['pandas==1.3.1']

setup_kwargs = {
    'name': 'tscalcs',
    'version': '0.1.0.dev1',
    'description': 'Package to operate time series math operations as if they were normal python variables.',
    'long_description': '# tscalcs\n\n',
    'author': 'Pedro H. Thompson Furtado',
    'author_email': 'thompsonp17@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://codigo-externo.petrobras.com.br/simu/tscalcs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
