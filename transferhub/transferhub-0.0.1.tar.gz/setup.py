# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['transferhub']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'transferhub',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'JanSeidlein',
    'author_email': 'jan@dmesh.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
