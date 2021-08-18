# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiodeta']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'aiodeta',
    'version': '0.1.1',
    'description': 'Unofficial Deta client',
    'long_description': '# aiodeta\n\n[![Build](https://github.com/leits/aiodeta/actions/workflows/testing.yml/badge.svg?branch=main)](https://github.com/leits/aiodeta/actions/workflows/testing.yml)\n[![codecov](https://codecov.io/gh/leits/aiodeta/branch/main/graph/badge.svg?token=2W3AhfHpPT)](https://codecov.io/gh/leits/aiodeta)\n\nUnofficial client for Deta Clound\n\n## Supported functionality\n\n- [x] Deta Base\n- [ ] Deta Drive\n- [ ] Decorator for cron tasks\n\n## Examples\n\n```python\nimport asyncio\nimport aiobotocore\n\nDETA_PROJECT_KEY = "xxx_yyy"\n\n\nasync def go():\n    db_name = "users"\n\n    # Initialize Deta client\n    deta = Deta(DETA_PROJECT_KEY)\n\n    # Initialize Deta Base client\n    base = deta.Base(db_name)\n\n    # Create row in Deta Base\n    user = {"username": "steve", "active": False}\n    resp = await base.insert(user)\n    print(resp)\n    user_key = resp["key"]\n\n    # Update row by key\n    resp = await base.update(user_key, set={"active": True})\n    print(resp)\n\n    # Get row by key\n    resp = await base.get(user_key)\n    print(resp)\n\n    # Delete row by key\n    resp = await base.delete(user_key)\n    print(resp)\n\n    # Create multiple rows in one request\n    users = [\n        {"username": "jeff", "active": True},\n        {"username": "rob", "active": False},\n        {"username": "joe", "active": True}\n    ]\n    resp = await base.put(users)\n    print(resp)\n\n    # Query data\n    query = [{"active": True}, {"username?pfx": "j"}]\n    result = await base.query(query=query, limit=10)\n    print(result)\n\n    # Close connection\n    await deta.close()\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(go())\n```\n',
    'author': 'leits',
    'author_email': 'leits.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/leits/aiodeta',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
