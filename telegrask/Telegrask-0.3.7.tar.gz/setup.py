# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['telegrask', 'telegrask.cli', 'telegrask.cli.templates', 'telegrask.ext']

package_data = \
{'': ['*']}

install_requires = \
['python-telegram-bot>=13.7,<14.0']

setup_kwargs = {
    'name': 'telegrask',
    'version': '0.3.7',
    'description': 'Flask-inspired Telegram bot micro framework for Python.',
    'long_description': '# Telegrask\n\n![status](https://img.shields.io/pypi/status/telegrask?style=flat-square)\n[![package version](https://img.shields.io/pypi/v/telegrask?style=flat-square)](https://pypi.org/project/Telegrask)\n[![downloads](https://img.shields.io/pypi/dd/telegrask?style=flat-square)](https://pypi.org/project/Telegrask)\n[![license](https://img.shields.io/github/license/samedamci/telegrask?style=flat-square)](https://github.com/samedamci/telegrask/blob/master/LICENSE)\n[![docs](https://readthedocs.org/projects/telegrask/badge/?version=stable&style=flat-square)](https://telegrask.rtfd.io)\n[![code style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)\n\n---\n\nFlask-inspired Telegram bot micro framework for Python.\nMain idea is to use callback function decorators and make bot\ncreating more intuitive for developer.\n\n## Installing\n\n```shell\n$ python3 -m pip install Telegrask\n```\n\n---\n\n## Simple "Hello World" bot example\n\n```python\nfrom telegrask import Telegrask\n\nbot = Telegrask("BOT_TOKEN")\n\n\n@bot.command("hello", help=\'display "Hello, World!"\')\ndef hello_command(update, context):\n    update.message.reply_text("Hello, World!")\n\n\nif __name__ == "__main__":\n    bot.run(debug=True)\n```\n\nMore examples in [examples](./examples) folder.\n\n## Equivalent in pure [python-telegram-bot](https://python-telegram-bot.org/)\n\n<details>\n<summary>Click to show</summary>\n\n```python\nfrom telegram.ext import Updater, CommandHandler\nfrom telegram import ParseMode\nimport logging\n\nlogging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)\nlogger = logging.getLogger(__name__)\n\n\ndef hello_command(update, context):\n    update.message.reply_text("Hello, World!")\n\n\ndef help_command(update, context):\n    help_content = """*Available commands*\n\n/hello\ndisplay "Hello, World!"\n\n/help\ndisplay this message\n"""\n    update.message.reply_text(help_content, parse_mode=ParseMode.MARKDOWN)\n\n\ndef main():\n    global updater\n    updater = Updater("BOT_TOKEN")\n    dispatcher = updater.dispatcher\n    dispatcher.add_handler(CommandHandler("hello", hello_command))\n    dispatcher.add_handler(CommandHandler(["help", "start"], help_command))\n    updater.start_polling()\n    updater.idle()\n\n\nif __name__ == "__main__":\n    main()\n```\n\n</details>\n\n---\n\n## Useful links\n\n- [Documentation](http://telegrask.rtfd.io/)\n- [PyPI Releases](https://pypi.org/project/Telegrask/)\n',
    'author': 'samedamci',
    'author_email': 'samedamci@disroot.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/samedamci/telegrask',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
