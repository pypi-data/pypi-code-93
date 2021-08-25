# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notion', 'notion.endpoints']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.15.0', 'pydantic[email]>=1.7']

setup_kwargs = {
    'name': 'notion-sdk',
    'version': '0.7.0',
    'description': 'A simple and easy to use Python client for the Notion API',
    'long_description': '<p align="center">\n    <div align="center">\n        <h1>Notion SDK for Python</h1>\n        <p>\n            <b>A simple and easy to use Python client for the <a href="https://developers.notion.com">Notion API</a> </b>\n        </p>\n        <a href="https://pypi.org/project/notion-sdk/"><img src="https://badge.fury.io/py/notion-sdk.svg" alt="PyPI version" height="18"></a>\n        <a href="https://github.com/getsyncr/notion-sdk/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License" height="18"></a>\n        <a href="https://pepy.tech/project/notion-sdk"><img alt="Downloads" src="https://pepy.tech/badge/notion-sdk"></a>\n        <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n    </div>\n</p>\n\n`Notion SDK` is a fully typed Python library to use the Notion API. It supports asyncio.\nIt uses the great [httpx](https://github.com/encode/httpx) as an HTTP client and [pydantic](https://github.com/samuelcolvin/pydantic)\nfor data validation and typing. This client is meant to be a Python version of the reference [JavaScript SDK](https://github.com/makenotion/notion-sdk-js), so usage should be pretty similar between both.\n\n## Installation\n\n```shell\n$ pip install notion-sdk\n```\n\n## Usage\n\nImport and initialize a client using an **integration token** or an OAuth **access token**.\n\n```python\nfrom notion import NotionClient\n\nnotion = NotionClient(auth="YOUR_ACCESS_TOKEN")\n\ndef fetch_databases() -> None:\n    response = notion.databases.list()\n    for database in response.results:\n        print(database.title)\n\nif __name__ == "__main__":\n    fetch_databases()\n```\n\nMore example are available in the [examples](examples) folder.\n\n## Async Usage\n\nThis library supports asynchronous calls to Notion API.\n\nEach method returns a `Coroutine` that have to be awaited to retreive the typed response.\n\nThe same methods are available for sync or async but you have to use the `NotionAsyncClient` like\nin the following example:\n\n```python\nimport asyncio\n\nfrom notion import NotionAsyncClient\n\nnotion = NotionAsyncClient(auth="YOUR_ACCESS_TOKEN")\n\nasync def fetch_databases() -> None:\n    response = await notion.databases.list()\n    for database in response.results:\n        print(database.title)\n\nif __name__ == "__main__":\n    asyncio.run(fetch_databases())\n```\n\n## Clients options\n\n`NotionClient` and `NotionAsyncClient` support the following options on initialization.\nThese options are all keys in the single constructor parameter.\n\n<!-- markdownlint-disable -->\n| Option | Default value | Type | Description |\n|--------|---------------|---------|-------------|\n| `auth` | `None` | `string` | Bearer token for authentication. If left undefined, the `auth` parameter should be set on each request. |\n| `timeout` | `60` | `int` | Number of seconds to wait before emitting a `RequestTimeoutError` |\n| `base_url` | `"https://api.notion.com/v1/"` | `string` | The root URL for sending API requests. This can be changed to test with a mock server. |\n| `user_agent` | `notion-sdk/VERSION (https://github.com/getsyncr/notion-sdk)` | `string` | A custom user agent send with every request. |\n<!-- markdownlint-enable -->\n\n## Requirements\n\nThis package supports the following minimum versions:\n\n* Python >= `3.7`\n* `httpx` >= `0.15.0`\n* `pydantic` >= `1.7`\n\nEarlier versions may still work, but we encourage people building new applications\nto upgrade to the current stable.\n\n## License\n\nDistributed under the Apache License. See [LICENSE](LICENSE) for more information.\n',
    'author': 'Nicolas Lecoy',
    'author_email': 'nicolas@syncr.so',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://syncr.so',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
