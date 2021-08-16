# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ldict', 'ldict.abs', 'ldict.abs.mixin']

package_data = \
{'': ['*']}

install_requires = \
['garoupa>=2.210811.7,<3.0.0',
 'orjson>=3.5.0,<4.0.0',
 'uncompyle6>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'ldict',
    'version': '2.210815.1',
    'description': 'Lazy dict with universaly unique identified values',
    'long_description': None,
    'author': 'davips',
    'author_email': 'dpsabc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
