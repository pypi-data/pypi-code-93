# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paperpile_notion']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'emojis>=0.6.0,<0.7.0',
 'notion-database>=20210513.7,<20210514.0',
 'notion>=0.0.28,<0.0.29',
 'pandas>=1.3.2,<2.0.0',
 'ruamel.yaml>=0.17.13,<0.18.0']

entry_points = \
{'console_scripts': ['paperpile-notion = paperpile_notion.commands:cli']}

setup_kwargs = {
    'name': 'paperpile-notion',
    'version': '0.2.0',
    'description': 'Sync Notion with Paperpile',
    'long_description': '# Paperpile Notion Integration\n\nInspired by [gsarti/paperpile-notion][gsarti]. This is a Python CLI to manually\nsync your articles in Paperpile to a Notion database. Optionally, you may sync\nan authors database as well.\n\n**NOTE:** This will only be maintained if Paperpile doesn\'t integrate directly\nwith Notion. They have expressed interest, [here][forum.paperpile/notion].\n\n[gsarti]: https://github.com/gsarti/paperpile-notion\n[forum.paperpile/notion]: https://forum.paperpile.com/t/suggestion-for-notion-hook/\n\nThis is a work in progress, and is currently intended for personal use only (no support, no warranty, no liability, etc.).\n\n## Installation\n\nYou can `pip` install `paperpile-notion`, **preferably in a virtual environment**.\n\n```bash\npip install paperpile-notion\n```\n\n## Requirements\n\nTo use `paperpile-notion`, you\'ll need a few things:\n\n1. A `JSON` export from Paperpile. You can retrieve this by going to "Settings >\n   Export > Export to JSON".\n1. A configuration file, similar to what you\'ll find in\n   [`docs/config.yml`][config]. **Currently, we do not support venues, but it is\n   planned.**\n1. Your `Article` database URL, which you can copy directly from your browser.\n1. (**optional**) Your `Author` database URL, copied in a similar way as above.\n1. Your `token_v2` (detailed below) **OR** your email/password (never stored by\n   `paperpile-notion`).\n\n**NOTE:** Your `Article` database __must have the following columns:__\n\n| Name | Type | Description |\n| ---- | ---- | ------------|\n| ID   | `text` | An ID issued by Paperpile which can be used to uniquely identify papers, feel free to hide the column in Notion once created. |\n| Status | `select` | Your reading status. Can be fully customized in your `config.yml`. |\n| Authors | `multi_select` OR `relation` | The paper\'s authors. If you have an `Author` database, use the `relation` type otherwise a `multi_select`. |\n| URL | `url` | A link to the paper in Paperpile. |\n| Fields | `multi_select` | The [sub-]fields the paper belongs to. |\n| Methods | `multi_select` | The methods/tools used in the paper. |\n\n[config]: docs/config.yml\n\n## Usage\n\nAs we use `notion-py`, we are limited by their support for either an\nemail/password login OR your `TOKEN_V2`. Your `token_v2` may be retrieved from\nyour [notion.so][notion] cookies.\n\n1. [Using your `token_v2` (recommended)](#token-v2)\n1. [Using your email/password](#email-pass)\n\n<i id="token-v2"></i>\n### Using your `token_v2` (recommended)\n\nYou have two ways to supply your `token_v2` to `paperpile-notion`:\n1. (**preferred**) You may store it in an environment variable called\n   `NOTION_TOKEN_V2`, which will be read by `paperpile-notion`.\n1. **OR** you may pass your token in using the `--token <token_v2>` flag.\n\n```bash\n# Using NOTION_TOKEN_V2\n$ paperpile-notion update-db --refs <YOUR_JSON>.json\n\n# Using --token ...\n$ paperpile-notion --token <token_v2> update-db --refs <YOUR_JSON>.json\n```\n\n<i id="email-pass"></i>\n### Using your email/password\n\nYou will be prompted each time for your Notion email/password login.\n\n```bash\npaperpile-notion update-db --refs <YOUR_JSON>.json\n```\n\n\n### Example output\n\nWhen adding, adding a new paper to the database:\n\n![Console output](img/output.png)\n\nExample resulting database on Notion:\n\n![Notion result](img/notion_result.png)\n',
    'author': 'J Muchovej',
    'author_email': '5000729+jmuchovej@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jmuchovej/paperpile-notion',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
