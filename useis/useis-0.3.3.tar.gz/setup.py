# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['useis',
 'useis.clients',
 'useis.clients.old_api_client',
 'useis.core',
 'useis.processors',
 'useis.settings',
 'useis.tools']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.4,<4.0.0',
 'ipdb>=0.13.9,<0.14.0',
 'tqdm>=4.59.0,<5.0.0',
 'uquake>=0.6.2,<0.7.0']

setup_kwargs = {
    'name': 'useis',
    'version': '0.3.3',
    'description': '',
    'long_description': None,
    'author': 'jpmercier',
    'author_email': 'jpmercier01@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
