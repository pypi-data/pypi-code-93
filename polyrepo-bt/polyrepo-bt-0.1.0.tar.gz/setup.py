# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbt']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.6.3,<4.0.0', 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'polyrepo-bt',
    'version': '0.1.0',
    'description': 'A build tool for poetry packages (living in submodules of a Git repo)',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
