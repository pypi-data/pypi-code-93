# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jetblack_tweeter',
 'jetblack_tweeter.api',
 'jetblack_tweeter.clients',
 'jetblack_tweeter.clients.aiohttp',
 'jetblack_tweeter.clients.bareclient']

package_data = \
{'': ['*']}

install_requires = \
['oauthlib>=3.1,<4.0']

extras_require = \
{'aiohttp': ['aiohttp>=3.7,<4.0'], 'bareclient': ['bareclient>=4.6,<5.0']}

setup_kwargs = {
    'name': 'jetblack-tweeter',
    'version': '0.4.0',
    'description': 'An asyncio twitter client',
    'long_description': '# jetblack-tweeter\n\nA Python 3.8 asyncio twitter client.\n\nThis Twitter client is designed to support arbitrary HTTP clients. There is\ncurrently support for\n[bareClient](https://rob-blackbourn.github.io/bareClient/api/bareclient/)\nand [aiohttp](https://docs.aiohttp.org/en/stable/index.html).\n\n## Status\n\nThis is work in progress, but functional.\n\nThere is currently limited support for streaming, statuses and accounts. Only the 1.1 api is currently implemented.\n\n## Installation\n\nInstall with `pip`, specifying the HTTP backend you wish to use.\n\nFor bareClient:\n\n```bash\npip install jetblack-tweeter[bareclient]\n```\n\nFor aiohttp:\n\n```bash\npip install jetblack-tweeter[aiohttp]\n```\n\n## Usage\n\nHere is an example:\n\n```python\nimport asyncio\nimport os\n\nfrom jetblack_tweeter import Tweeter\nfrom jetblack_tweeter.clients.bareclient import BareTweeterSession\n\n# Get the secrets from environment variables.\nAPP_KEY = os.environ["APP_KEY"]\nAPP_KEY_SECRET = os.environ["APP_KEY_SECRET"]\nACCESS_TOKEN = os.environ["ACCESS_TOKEN"]\nACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]\n\n\nasync def main():\n    tweeter = Tweeter(\n        BareTweeterSession(),\n        APP_KEY,\n        APP_KEY_SECRET,\n        # Optional for user authentication.\n        access_token=ACCESS_TOKEN,\n        access_token_secret=ACCESS_TOKEN_SECRET\n    )\n\n    user_timeline = await tweeter.statuses.user_timeline()\n    print(user_timeline)\n\n    account_settings = await tweeter.account.settings()\n    print(account_settings)\n\n    account_verify_credentials = await tweeter.account.verify_credentials()\n    print(account_verify_credentials)\n\n    # Watch the random sampling of tweets chosen by twitter\n    async for tweet in tweeter.stream.sample():\n        print(tweet)\n\n    # Stream tweets which have the tag "#python" from New York\n    # and San Francisco.\n    async for tweet in tweeter.stream.filter(\n            track=[\'#python\'],\n            locations=[\n                ((-122.75, 36.8), (-121.75, 37.8)),\n                ((-74, 40), (-73, 41))\n            ]\n    ):\n        print(tweet)\n\n    result = await tweeter.statuses.update(\'Hello from jetblack-tweeter\')\n    print(result)\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```\n',
    'author': 'Rob Blackbourn',
    'author_email': 'rob.blackbourn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rob-blackbourn/jetblack-tweeter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
