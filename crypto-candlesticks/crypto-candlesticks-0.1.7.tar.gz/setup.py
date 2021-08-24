# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['crypto_candlesticks',
 'crypto_candlesticks.exchanges',
 'crypto_candlesticks.symbols']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<9.0.0',
 'importlib-metadata>=3.3,<5.0',
 'pandas>=1.0.5,<2.0.0',
 'requests>=2.24.0,<3.0.0',
 'retry>=0.9.2,<0.10.0',
 'rich>=9.6.2,<11.0.0']

entry_points = \
{'console_scripts': ['crypto-candlesticks = '
                     'crypto_candlesticks.interface:main']}

setup_kwargs = {
    'name': 'crypto-candlesticks',
    'version': '0.1.7',
    'description': 'Download candlestick data fast & easy for analysis',
    'long_description': '# crypto-candlesticks 📈\n\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n![Tests](https://github.com/Corfucinas/crypto-candlesticks/workflows/Tests/badge.svg)\n![Codecov](https://github.com/Corfucinas/crypto-candlesticks/workflows/Codecov/badge.svg)\n[![Documentation Status](https://readthedocs.org/projects/crypto-candlesticks/badge/?version=latest)](https://crypto-candlesticks.readthedocs.io/en/latest/?badge=latest)\n[![PyPI](https://img.shields.io/pypi/v/crypto-candlesticks.svg)](https://pypi.org/project/crypto-candlesticks/)\n[![Downloads](https://pepy.tech/badge/crypto-candlesticks)](https://pepy.tech/project/crypto-candlesticks)\n\n![gif-animation](media/animation.gif)\n\n---\n\nThe goal behind this project is to facilitate downloading cryptocurrency candlestick data fast & simple.\nCurrently only the [Bitfinex](https://www.bitfinex.com/) exchange is supported with more to come in future releases.\n\nThe command-line interface is built using [Click](https://click.palletsprojects.com/en/7.x/), which is intuitive and will prompt you for the commands.\n\nOnce the data is downloaded, it will be converted and stored in a `.csv, .sqlite3 and .pickle` file for convenient analysis.\nThe data will include the `Open, High, Low, Close` of the candles and the `volume` during the `interval` and its `timestamp`.\n\nSee [documentation](https://crypto-candlesticks.readthedocs.io/) and [Github repository](https://github.com/Corfucinas/crypto-candlesticks/).\n\n## Installation\n\nTo install the Crypto-candlesticks project,\nrun this command in your terminal:\n\n```bash\n   pip install crypto-candlesticks\n```\n\nOr if you are using [Poetry](https://python-poetry.org/)\n\n```bash\n    poetry add crypto-candlesticks\n```\n\n### Usage\n\ncrypto-candlesticks can be used the following way:\n\n```bash\n    $ crypto-candlesticks\n    "Welcome, what data do you wish to download?"\n```\n\nWhich will prompt the following:\n\n```text\n    Cryptocurrency symbol to download (ie. BTC, ETH, LTC):\n    Base pair:\n    Interval to download the candlestick data:\n    Date to start downloading the data (ie. YYYY-MM-DD):\n    Date up to the data will be downloaded (ie. YYYY-MM-DD):\n```\n\nOr you can pass the arguments yourself and skip the prompt:\n\n```text\n   crypto-candlesticks [OPTIONS]\n\n   -s <symbol>, --symbol <symbol>\n\n   The ticker you wish to download,\n   currently, only data from the Bitfinex exchange\n   is supported.\n   (e.g. [BTC|ETH|LTC] etc.)\n\n   -b <base currency>, --base_currency <base currency>\n\n    The base pair for the ticker.\n    (e.g. [USD|USDT|EUR|CNHT|GBP|JPY|DAI|BTC|EOS|ETH|XCHF|USTF0])\n\n   -i <interval>, --interval <interval>\n\n    The interval for each bar.\n    (e.g. [1m|5m|15m|30m|1h|3h|6h|12h|1D|7D|14D|1M])\n\n   -sd <start date>, --start_date <start date>\n\n    YYYY, MM, DD from which the candlestick data\n    will start.\n    (e.g. [2018-01-01])\n\n   -ed <end date>, --end date <end date>\n\n    YYYY, MM, DD up to which the candlestick\n    data will be downloaded.\n    (e.g. [2020-01-01])\n\n   --help\n\n   Display a short usage message and exit.\n```\n\n#### Example output for CSV ✅\n\n| Open     | Close     | High   | Low       | Volume    | Ticker  | Date       | Time     |\n| -------- | --------- | ------ | --------- | --------- | ------- | ---------- | -------- |\n| 7203     | 7201      | 7203.7 | 7200.1    | 9.404174  | BTC/USD | 12/31/2019 | 16:00:00 |\n| 7201     | 7223.6    | 7223.6 | 7201      | 7.9037398 | BTC/USD | 12/31/2019 | 16:01:00 |\n| 7224.4   | 7225      | 7225.5 | 7224.4    | 0.4799298 | BTC/USD | 12/31/2019 | 16:02:00 |\n| 7224.981 | 7225.9    | 7225.9 | 7224.981  | 0.9294573 | BTC/USD | 12/31/2019 | 16:03:00 |\n| 7225.862 | 7225.7295 | 7225.9 | 7225.7295 | 0.2913202 | BTC/USD | 12/31/2019 | 16:04:00 |\n| 7225.7   | 7225.8673 | 7225.9 | 7225.2973 | 1.0319704 | BTC/USD | 12/31/2019 | 16:05:00 |\n\n#### Example output for SQL (the timestamp is shown in milliseconds) ✅\n\n| ID  | Timestamp       | Open          | Close         | High          | Low           | Volume     | Ticker | Interval |\n| --- | --------------- | ------------- | ------------- | ------------- | ------------- | ---------- | ------ | -------- |\n| 1   | 1577868000000.0 | 7205.7        | 7205.8        | 7205.8        | 7205.7        | 0.07137942 | BTCUSD | 1m       |\n| 2   | 1577867940000.0 | 7205.70155305 | 7205.8        | 7205.8        | 7205.70155305 | 0.035      | BTCUSD | 1m       |\n| 3   | 1577867880000.0 | 7205.7        | 7205.70155305 | 7205.70155305 | 7205.7        | 0.025      | BTCUSD | 1m       |\n| 4   | 1577867820000.0 | 7205.75299748 | 7205.75299748 | 7205.75299748 | 7205.7        | 0.075      | BTCUSD | 1m       |\n| 5   | 1577867760000.0 | 7205.75299748 | 7205.2        | 7206.3        | 7205.2        | 0.005      | BTCUSD | 1m       |\n| 6   | 1577867700000.0 | 7205.2        | 7205.2        | 7205.2        | 7205.2        | 4.5802     | BTCUSD | 1m       |\n\n##### Contributing\n\nFeel free to open an [issue](https://github.com/Corfucinas/crypto-candlesticks/issues/new) or [pull request](https://github.com/Corfucinas/crypto-candlesticks/pulls).\n\n##### Buy me a coffee\n\nETH: 0x06Acb31587a96808158BdEd07e53668d8ce94cFE\n',
    'author': 'Pedro Torres',
    'author_email': 'corfucinas@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://crypto-candlesticks.readthedocs.io/en/latest/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
