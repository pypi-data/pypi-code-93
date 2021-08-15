# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hannah', 'hannah.http', 'hannah.tests']

package_data = \
{'': ['*']}

install_requires = \
['cached-property>=1.5.2,<2.0.0', 'httpx>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'hannah',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'suganthsundar',
    'author_email': 'suganthsundar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
