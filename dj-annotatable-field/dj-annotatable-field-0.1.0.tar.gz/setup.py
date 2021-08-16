# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dj_annotatable_field']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2.6,<4.0.0']

setup_kwargs = {
    'name': 'dj-annotatable-field',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'massover',
    'author_email': 'joshm@simplebet.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
