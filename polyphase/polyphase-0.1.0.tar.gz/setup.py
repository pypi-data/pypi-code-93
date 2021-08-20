# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['polyphase']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'polyphase',
    'version': '0.1.0',
    'description': 'Polyphase channelizer implement using Python.',
    'long_description': None,
    'author': 'Jackie Wang',
    'author_email': 'falwat@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
