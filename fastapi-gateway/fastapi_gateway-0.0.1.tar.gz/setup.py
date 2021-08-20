# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_gateway', 'fastapi_gateway.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'ujson>=4.1.0,<5.0.0']

setup_kwargs = {
    'name': 'fastapi-gateway',
    'version': '0.0.1',
    'description': 'FastAPI gateway for microservices.',
    'long_description': '# fastapi-gateway\n⚙️ Async single entry point for microservices.\n',
    'author': 'dotX12',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dotX12/fastapi-gateway',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
