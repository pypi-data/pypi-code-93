# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pygeoapi_mssql_provider']

package_data = \
{'': ['*']}

install_requires = \
['pygeoapi>=0.10.1,<0.11.0', 'pymssql>=2.2.2,<3.0.0']

setup_kwargs = {
    'name': 'pygeoapi-mssql-provider',
    'version': '0.2.0',
    'description': 'Feature providor for the pygeoapi service',
    'long_description': None,
    'author': 'maarten-betman',
    'author_email': 'mbetman@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
