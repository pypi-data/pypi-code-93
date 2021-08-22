# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['useis',
 'useis.clients',
 'useis.clients.old_api_client',
 'useis.core',
 'useis.processors',
 'useis.settings']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.4,<4.0.0',
 'myst-parser>=0.15.1,<0.16.0',
 'rinohtype>=0.5.3,<0.6.0',
 'tqdm>=4.59.0,<5.0.0',
 'uquake>=0.6.57,<0.7.0']

extras_require = \
{':extra == "docs"': ['Sphinx>=4.1.2,<5.0.0', 'sphinx-rtd-theme>=0.5.2,<0.6.0']}

setup_kwargs = {
    'name': 'useis',
    'version': '0.6.1',
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
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
