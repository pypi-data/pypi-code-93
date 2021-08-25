# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cls_client', 'cls_client.shared']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0']

setup_kwargs = {
    'name': 'cls-client',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
