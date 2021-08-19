# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyrthomas']

package_data = \
{'': ['*'], 'pyrthomas': ['UNKNOWN.egg-info/*']}

install_requires = \
['networkx>=2.0', 'pydot>=1.4.2,<2.0.0']

setup_kwargs = {
    'name': 'pyrthomas',
    'version': '0.0.10',
    'description': "Python implementation for René Thomas's Framework",
    'long_description': "Python implementation for Rene` Thomas's Framework\n\nFor installation execute\n\n`pip install pyrthomas`\n\nTo learn how to use this package please check examples directory.\n\n",
    'author': 'Talha Junaid',
    'author_email': 'talhajunaidd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/talhajunaidd/pyrthomas',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
