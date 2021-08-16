# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spock']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyspock',
    'version': '0.1.0',
    'description': 'Python implementation for spock framework',
    'long_description': '# spock\n',
    'author': 'ZhengYu, Xu',
    'author_email': 'zen-xu@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
