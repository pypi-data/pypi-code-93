# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['char_pic']

package_data = \
{'': ['*']}

install_requires = \
['cowpy>=1.1.0,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'char-pic',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'xiaodeng',
    'author_email': 'xiaodengteacher@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
