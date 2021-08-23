# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shutup']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'shutup',
    'version': '0.1.2',
    'description': 'Stop python warnings, no matter what!',
    'long_description': None,
    'author': 'Fred Israel',
    'author_email': 'fredpublico@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
