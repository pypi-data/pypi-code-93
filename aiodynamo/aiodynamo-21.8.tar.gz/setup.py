# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aiodynamo', 'aiodynamo.http']

package_data = \
{'': ['*']}

install_requires = \
['yarl>=1.4.2,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['typing_extensions>=3.7,<4.0'],
 'aiohttp': ['aiohttp>=3.6.2,<4.0.0'],
 'httpx': ['httpx>=0.11.1,<1.0.0']}

setup_kwargs = {
    'name': 'aiodynamo',
    'version': '21.8',
    'description': 'Asyncio DynamoDB client',
    'long_description': '# AsyncIO DynamoDB\n\n[![CircleCI](https://circleci.com/gh/HENNGE/aiodynamo.svg?style=svg)](https://circleci.com/gh/HENNGE/aiodynamo)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Documentation Status](https://readthedocs.org/projects/aiodynamo/badge/?version=latest)](https://aiodynamo.readthedocs.io/en/latest/?badge=latest)\n\nAsynchronous pythonic DynamoDB client; **2x** faster than `aiobotocore/boto3/botocore`.\n\n## Quick start\n\n### With httpx\nInstall this library\n\n`pip install "aiodynamo[httpx]"` or, for poetry users `poetry add aiodynamo -E httpx`\n\nConnect to DynamoDB\n\n```py\nfrom aiodynamo.client import Client\nfrom aiodynamo.credentials import Credentials\nfrom aiodynamo.http.httpx import HTTPX\nfrom httpx import AsyncClient\n\n    async with AsyncClient() as h:\n        client = Client(HTTPX(h), Credentials.auto(), "us-east-1")\n```\n\n### With aiohttp\nInstall this library\n\n`pip install "aiodynamo[aiohttp]"` or, for poetry users `poetry add aiodynamo -E aiohttp`\n\nConnect to DynamoDB\n\n```py\nfrom aiodynamo.client import Client\nfrom aiodynamo.credentials import Credentials\nfrom aiodynamo.http.aiohttp import AIOHTTP\nfrom aiohttp import ClientSession\n\n    async with ClientSession() as session:\n        client = Client(AIOHTTP(session), Credentials.auto(), "us-east-1")\n```\n\n### API use\n\n```py\n        table = client.table("my-table")\n\n        # Create table if it doesn\'t exist\n        if not await table.exists():\n            await table.create(\n                Throughput(read=10, write=10),\n                KeySchema(hash_key=KeySpec("key", KeyType.string)),\n            )\n\n        # Create or override an item\n        await table.put_item({"key": "my-item", "value": 1})\n        # Get an item\n        item = await table.get_item({"key": "my-item"})\n        print(item)\n        # Update an item, if it exists.\n        await table.update_item(\n            {"key": "my-item"}, F("value").add(1), condition=F("key").exists()\n        )\n```\n\n## Why aiodynamo\n\n* boto3 and botocore are synchronous. aiodynamo is built for **asynchronous** apps.\n* aiodynamo is **fast**. Two times faster than aiobotocore, botocore or boto3 for operations such as query or scan.\n* aiobotocore is very low level. aiodynamo provides a **pythonic API**, using modern Python features. For example, paginated APIs are automatically depaginated using asynchronous iterators.\n* **Legible source code**. botocore and derived libraries generate their interface at runtime, so it cannot be inspected and isn\'t typed. aiodynamo is hand written code you can read, inspect and understand.\n* **Pluggable HTTP client**. If you\'re already using an asynchronous HTTP client in your project, you can use it with aiodynamo and don\'t need to add extra dependencies or run into dependency resolution issues.\n\n[Complete documentation is here](https://aiodynamo.readthedocs.io/)\n',
    'author': 'Jonas Obrist',
    'author_email': 'jonas.obrist@hennge.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/HENNGE/aiodynamo',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
