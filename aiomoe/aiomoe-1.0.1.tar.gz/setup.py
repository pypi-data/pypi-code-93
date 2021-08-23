# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiomoe', 'aiomoe.api', 'aiomoe.errors', 'aiomoe.models', 'aiomoe.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'loguru>=0.5.3,<0.6.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'aiomoe',
    'version': '1.0.1',
    'description': 'Fully asynchronous trace.moe API wrapper',
    'long_description': '# AioMoe\n\nFully asynchronous trace.moe API wrapper\n\n## Installation\n\nYou can install the stable version from PyPI:\n\n    $ pip install aiomoe\n\nOr get it from github:\n\n    $ pip install https://github.com/FeeeeK/aiomoe/archive/refs/heads/master.zip\n\n## Usage\n\n### Get info about your account\n\n```python\nimport asyncio\nfrom aiomoe import AioMoe\n\ntm = AioMoe() # or AioMoe(token="xxxxxxxx")\n\nasync def main():\n    me = await tm.me()\n    print(me)\n    print(f"Used quota: {me.quota_used}/{me.quota}")\n\nasyncio.run(main())\n```\nThe output will be like this:\n```\nUser(error=None, id=\'your ip\', priority=0, concurrency=1, quota=1000, quota_used=0)\nUsed quota: 0/1000\n```\n\n### Search anime\n```python\nimport asyncio\nfrom aiomoe import AioMoe\n\ntm = AioMoe()\n\nasync def main():\n    image = "https://i.imgur.com/Xrb06w5.png"\n    search_results = await tm.search(file_source=image, anilist_info=True)\n    print(search_results.result[0].anilist.title.romaji)\n    # \'Steins;Gate 0\'\n\nasyncio.run(main())\n```\nYou can pass a link to an image, bytes or file-like object (`io.BytesIO`)\n```python\n    with open("image.png", "rb") as file:\n        search_results = await tm.search(file)\n```\nAnd use additional parameters such as:\n - anilist_info - Return an `Anilist` object instead of anilist id\n - cut_borders - Cut out black borders from screenshots\n - anilist_id - Filter results by anilist id\n\n## See Also\n  - [Response objects](https://github.com/FeeeeK/aiomoe/blob/master/aiomoe/models/models.py)\n  - [trace.moe API docs](https://soruly.github.io/trace.moe-api/#/docs)\n  - [trace.moe API swagger docs](https://app.swaggerhub.com/apis/soruly/api.trace.moe)\n\n## Contributing\n\n1.  Fork it\n2.  Create your feature branch (`git checkout -b my-new-feature`)\n3.  Commit your changes (`git commit -am \'Add some feature\'`)\n4.  Push to the branch (`git push origin my-new-feature`)\n5.  Create new Pull Request\n\n## License\n\nReleased under the MIT license.\n\nCopyright by [FeeeeK](https://github.com/feeeek).\n',
    'author': 'FeeeeK',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FeeeeK/aiomoe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
