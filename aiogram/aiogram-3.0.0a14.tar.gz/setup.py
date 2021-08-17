# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiogram',
 'aiogram.client',
 'aiogram.client.session',
 'aiogram.dispatcher',
 'aiogram.dispatcher.event',
 'aiogram.dispatcher.filters',
 'aiogram.dispatcher.fsm',
 'aiogram.dispatcher.fsm.storage',
 'aiogram.dispatcher.handler',
 'aiogram.dispatcher.middlewares',
 'aiogram.methods',
 'aiogram.types',
 'aiogram.utils',
 'aiogram.utils.exceptions',
 'aiogram.utils.help']

package_data = \
{'': ['*']}

install_requires = \
['Babel>=2.9.1,<3.0.0',
 'aiofiles>=0.6.0,<0.7.0',
 'aiohttp>=3.7.4,<4.0.0',
 'async_lru>=1.0.2,<2.0.0',
 'magic-filter>=1.0.0,<2.0.0',
 'pydantic>=1.8.1,<2.0.0']

extras_require = \
{'docs': ['sphinx>=3.1.0,<4.0.0',
          'sphinx-intl>=2.0.1,<3.0.0',
          'sphinx-autobuild>=2020.9.1,<2021.0.0',
          'sphinx-copybutton>=0.3.1,<0.4.0',
          'furo>=2021.6.18-beta.36,<2022.0.0',
          'sphinx-prompt>=1.3.0,<2.0.0',
          'Sphinx-Substitution-Extensions>=2020.9.30,<2021.0.0'],
 'proxy': ['aiohttp-socks>=0.5.5,<0.6.0'],
 'redis': ['aioredis>=2.0.0,<3.0.0']}

setup_kwargs = {
    'name': 'aiogram',
    'version': '3.0.0a14',
    'description': 'Modern and fully asynchronous framework for Telegram Bot API',
    'long_description': '# aiogram 3.0 [WIP]\n\n[![\\[Telegram\\] aiogram live](https://img.shields.io/badge/telegram-aiogram-blue.svg?style=flat-square)](https://t.me/aiogram_live)\n[![MIT License](https://img.shields.io/pypi/l/aiogram.svg?style=flat-square)](https://opensource.org/licenses/MIT)\n[![Supported python versions](https://img.shields.io/pypi/pyversions/aiogram.svg?style=flat-square)](https://pypi.python.org/pypi/aiogram)\n[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-5.3-blue.svg?style=flat-square&logo=telegram)](https://core.telegram.org/bots/api)\n[![PyPi Package Version](https://img.shields.io/pypi/v/aiogram.svg?style=flat-square)](https://pypi.python.org/pypi/aiogram)\n[![PyPi status](https://img.shields.io/pypi/status/aiogram.svg?style=flat-square)](https://pypi.python.org/pypi/aiogram)\n[![Downloads](https://img.shields.io/pypi/dm/aiogram.svg?style=flat-square)](https://pypi.python.org/pypi/aiogram)\n[![Codecov](https://img.shields.io/codecov/c/github/aiogram/aiogram?style=flat-square)](https://app.codecov.io/gh/aiogram/aiogram)\n\n**aiogram** modern and fully asynchronous framework for [Telegram Bot API](https://core.telegram.org/bots/api) written in Python 3.8 with [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://github.com/aio-libs/aiohttp). It helps you to make your bots faster and simpler.\n',
    'author': 'Alex Root Junior',
    'author_email': 'jroot.junior@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://aiogram.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
