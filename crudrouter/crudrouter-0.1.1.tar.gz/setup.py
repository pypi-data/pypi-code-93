# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crudrouter', 'crudrouter.tinydb']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.62.0,<0.63.0',
 'loguru>=0.5.3,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'tinydb>=4.5.1,<5.0.0',
 'uuid>=1.30,<2.0',
 'uvicorn>=0.11.8,<0.12.0']

setup_kwargs = {
    'name': 'crudrouter',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Benjamin Harruff',
    'author_email': 'harruff.benjamin@solute.us',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://code.shipyard.blackpearl.us/bma/sscp/crudrouter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
