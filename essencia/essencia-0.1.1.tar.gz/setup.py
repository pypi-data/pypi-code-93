# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['essencia', 'essencia.deta', 'essencia.enumeration']

package_data = \
{'': ['*']}

install_requires = \
['deta>=1.0.0,<2.0.0', 'starlette>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'essencia',
    'version': '0.1.1',
    'description': 'Python3 package for use in essencia system.',
    'long_description': None,
    'author': 'Daniel Arantes',
    'author_email': 'arantesdv@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
