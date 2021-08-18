# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['owout']

package_data = \
{'': ['*']}

install_requires = \
['pyowo>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'owout',
    'version': '0.1.0',
    'description': 'Convert console output into owo.',
    'long_description': None,
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
