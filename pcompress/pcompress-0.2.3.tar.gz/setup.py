# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pcompress']

package_data = \
{'': ['*']}

install_requires = \
['gerrychain>=0.2.17,<0.3.0', 'pexpect>=4.8.0,<5.0.0']

setup_kwargs = {
    'name': 'pcompress',
    'version': '0.2.3',
    'description': 'Experimental, efficient, and performant binary representation of districting plans',
    'long_description': None,
    'author': 'Max Fan',
    'author_email': 'root@max.fan',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/InnovativeInventor/pcompress',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
