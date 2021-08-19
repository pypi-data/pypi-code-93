# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['great_text']

package_data = \
{'': ['*']}

install_requires = \
['pyfiglet>=0.8.post1,<0.9', 'termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'great-text',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Deepak',
    'author_email': 'info.deepakpatidar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
