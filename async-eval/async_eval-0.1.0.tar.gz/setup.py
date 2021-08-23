# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['async_eval', 'async_eval.ext', 'async_eval.ext.pydevd']

package_data = \
{'': ['*']}

install_requires = \
['nest-asyncio>=1.5.1,<2.0.0']

extras_require = \
{'all': ['pydevd-pycharm>=212.5080.18,<213.0.0', 'trio>=0.19.0,<0.20.0'],
 'pydevd-pycharm': ['pydevd-pycharm>=212.5080.18,<213.0.0'],
 'trio': ['trio>=0.19.0,<0.20.0']}

setup_kwargs = {
    'name': 'async-eval',
    'version': '0.1.0',
    'description': 'eval async code from sync',
    'long_description': None,
    'author': 'Yurii Karabas',
    'author_email': '1998uriyyo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
