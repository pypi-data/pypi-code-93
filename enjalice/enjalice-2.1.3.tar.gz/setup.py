# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enjalice', 'enjalice.attachments']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

extras_require = \
{'aiohttp': ['aiohttp[speedups]>=3.7.4,<4.0.0']}

setup_kwargs = {
    'name': 'enjalice',
    'version': '2.1.3',
    'description': 'EnjAlice is a asynchronous framework for Yandex Alice API',
    'long_description': None,
    'author': 'jotty',
    'author_email': 'bard143games@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
