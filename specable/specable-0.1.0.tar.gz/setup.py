# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['specable']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0']

setup_kwargs = {
    'name': 'specable',
    'version': '0.1.0',
    'description': 'dictionaries to objects and vice versa',
    'long_description': None,
    'author': 'Marcel Langer',
    'author_email': 'dev@marcel.science',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
