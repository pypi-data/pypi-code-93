# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tgfeed']

package_data = \
{'': ['*']}

install_requires = \
['Telethon>=1.22.0,<2.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'jsonpickle>=2.0.0,<3.0.0',
 'loguru>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'tgfeed',
    'version': '0.0.11',
    'description': 'Create feeds in Telegram easily',
    'long_description': None,
    'author': 'Nikolai',
    'author_email': 'magnickolas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
