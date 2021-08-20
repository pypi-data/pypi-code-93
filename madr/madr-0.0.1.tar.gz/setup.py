# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['madr']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'madr',
    'version': '0.0.1',
    'description': 'A comprehensive toolset around making and managing MADRs using source control',
    'long_description': None,
    'author': 'WilliamJohns',
    'author_email': 'will@wcj.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
