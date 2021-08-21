# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['commanderbot',
 'commanderbot.core',
 'commanderbot.core.bot',
 'commanderbot.core.bot.abc']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.3,<0.5.0', 'colorlog>=4.2.1,<5.0.0', 'discord.py>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'commanderbot',
    'version': '0.9.0',
    'description': 'A simple wrapper and CLI bootstrap for discord.py bots.',
    'long_description': '# CommanderBot CLI\n\nA simple wrapper and CLI bootstrap for discord.py bots.\n\n[![package-badge]](https://pypi.python.org/pypi/commanderbot/)\n[![version-badge]](https://pypi.python.org/pypi/commanderbot/)\n\n## Running your bot\n\nYou can run your own bot without writing any code.\n\nYou will need the following:\n\n1. Your own [Discord Application](https://discordapp.com/developers/applications) with a bot token.\n2. A [configuration file](#configuring-your-bot) for the bot.\n3. A Python 3.8+ environment with the `commanderbot` package installed.\n   - It is recommended to use a [virtual environment](https://docs.python.org/3/tutorial/venv.html) for this.\n   - Run `pip install commanderbot` to install the bot core package.\n4. (Optional) The `commanderbot-ext` package; if you are using any of the provided extensions.\n   - Run `pip install commanderbot-ext` to install the bot extensions package.\n\nThe first thing you should do is check the CLI help menu:\n\n```bash\npython -m commanderbot --help\n```\n\nThere are three ways to provide your bot token:\n\n1. (Recommended) As the `BOT_TOKEN` environment variable: `BOT_TOKEN=put_your_bot_token_here`\n2. As a CLI option: `--token put_your_bot_token_here`\n3. Manually, when prompted during start-up\n\nHere\'s an example that provides the bot token as an argument:\n\n```bash\npython -m commanderbot bot.json --token put_your_bot_token_here\n```\n\n## Configuring your bot\n\nThe current set of configuration options is limited. Following is an example configuration that sets the command prefix and loads the `status` and `faq` extensions.\n\n> Note that with this configuration, the `faq` extension will require read-write access to `faq.json` in the working directory.\n\n```json\n{\n  "command_prefix": ">",\n  "extensions": [\n    "commanderbot_ext.status",\n    {\n      "name": "commanderbot_ext.faq",\n      "enabled": true,\n      "options": {\n        "database": "faq.json",\n        "prefix": "?"\n      }\n    }\n  ]\n}\n```\n\n[package-badge]: https://img.shields.io/pypi/v/commanderbot.svg\n[version-badge]: https://img.shields.io/pypi/pyversions/commanderbot.svg\n',
    'author': 'Arcensoth',
    'author_email': 'arcensoth@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CommanderBot-Dev/commanderbot-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
