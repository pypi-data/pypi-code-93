# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trading_api_wrappers',
 'trading_api_wrappers.bitcoinity',
 'trading_api_wrappers.bitex',
 'trading_api_wrappers.bitfinex',
 'trading_api_wrappers.bitstamp',
 'trading_api_wrappers.buda',
 'trading_api_wrappers.coindesk',
 'trading_api_wrappers.coinmarketcap',
 'trading_api_wrappers.cryptomkt',
 'trading_api_wrappers.currencylayer',
 'trading_api_wrappers.kraken',
 'trading_api_wrappers.oxr',
 'trading_api_wrappers.ripio',
 'trading_api_wrappers.sfox',
 'trading_api_wrappers.surbtc']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.11.1,<2.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.26.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.6.4,<5.0.0']}

setup_kwargs = {
    'name': 'trading-api-wrappers',
    'version': '0.18.0',
    'description': 'Clients for popular Crypto Exchanges and other useful services',
    'long_description': '# Trading API Wrappers\n\n> Python 3.6+ clients for popular **Crypto Exchanges** and other useful services.\n\n> **Disclaimer:** Still at an early stage of development. Rapidly evolving APIs.\n\n[![PyPI - License](https://img.shields.io/pypi/l/trading-api-wrappers.svg)](https://opensource.org/licenses/MIT)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trading-api-wrappers.svg)\n[![PyPI](https://img.shields.io/pypi/v/trading-api-wrappers.svg)](https://pypi.org/project/trading-api-wrappers/)\n![PyPI - Status](https://img.shields.io/pypi/status/trading-api-wrappers.svg)\n[![Updates](https://pyup.io/repos/github/delta575/trading-api-wrappers/shield.svg)](https://pyup.io/repos/github/delta575/trading-api-wrappers/)\n\nSupported APIs:\n\n- [Buda](https://www.buda.com)\n- [Bitfinex](https://www.bitfinex.com)\n- [Bitstamp](https://www.bitstamp.net)\n- [CoinDesk](https://www.coindesk.com)\n- [CoinMarketCap](https://coinmarketcap.com)\n- [CryptoMKT](https://www.cryptomkt.com)\n- [Kraken](https://www.kraken.com)\n- [OpenExchangeRates](https://openexchangerates.org)\n\n## Installation\n\n### Requirements\n\n- Python 3.6+\n\nTo install, simply use `poetry` (or `pip`, of course):\n\n```bash\n$ poetry add trading-api-wrappers\n```\n\n### Dev setup\n\n```bash\n$ poetry install\n```\n\nRename `.env.example` to `.env` and configure your credentials (for tests)\n\n## Usage\n\n### Buda\n\nPublic API:\n\n```python\nfrom trading_api_wrappers import Buda\nclient = Buda.Public()\n```\n\nAuthenticated API:\n\n```python\nfrom trading_api_wrappers import Buda\nclient = Buda.Auth(API_KEY, API_SECRET)\n```\n\nBuda API Doc:\nhttps://api.buda.com\n\n### Bitfinex\n\nPublic API:\n\n```python\nfrom trading_api_wrappers import Bitfinex\nclient = Bitfinex.Public()\n```\n\nAuthenticated API:\n\n```python\nfrom trading_api_wrappers import Bitfinex\nclient = Bitfinex.Auth(API_KEY, API_SECRET)\n```\n\nBitfinex API Doc:\nhttps://bitfinex.readme.io/v1/docs\n\n### Bitstamp\n\nPublic API:\n\n```python\nfrom trading_api_wrappers import Bitstamp\nclient = Bitstamp.Public()\n```\n\nAuthenticated API:\n\n```python\nfrom trading_api_wrappers import Bitstamp\nclient = Bitstamp.Auth(API_KEY, API_SECRET, CUSTOMER_ID)\n```\n\nBitstamp API Doc:\nhttps://www.bitstamp.net/api\n\n### Kraken\n\nPublic API:\n\n```python\nfrom trading_api_wrappers import Kraken\nclient = Kraken.Public()\n```\n\nAuthenticated API:\n\n```python\nfrom trading_api_wrappers import Kraken\nclient = Kraken.Auth(API_KEY, API_SECRET)\n```\n\nKraken API Doc:\nhttps://www.kraken.com/help/api\n\n### CoinDesk\n\n```python\nfrom trading_api_wrappers import CoinDesk\nclient = CoinDesk()\n```\n\nCoinDesk API Doc:\nhttps://www.coindesk.com/api\n\n### CoinMarketCap\n\n```python\nfrom trading_api_wrappers import CoinMarketCap\nclient = CoinMarketCap()\n```\n\nCoinMarketCap API Doc:\nhttps://coinmarketcap.com/api\n\n### CryptoMKT\n\nPublic API:\n\n```python\nfrom trading_api_wrappers import CryptoMKT\nclient = CryptoMKT.Public()\n```\n\nAuthenticated API:\n\n```python\nfrom trading_api_wrappers import CryptoMKT\nclient = CryptoMKT.Auth(API_KEY, API_SECRET)\n```\n\nCryptoMKT API Doc:\nhttps://developers.cryptomkt.com\n\n### OpenExchangeRates\n\n```python\nfrom trading_api_wrappers import OXR\nclient = OXR(APP_ID)\n```\n\nOpenExchangeRates API Doc:\nhttps://docs.openexchangerates.org\n\n### CurrencyLayer\n\n```python\nfrom trading_api_wrappers import CurrencyLayer\nclient = CurrencyLayer(ACCESS_KEY)\n```\n\nCurrencyLayer API Doc:\nhttps://currencylayer.com/documentation\n\n## Licence\n\n[![PyPI - License](https://img.shields.io/pypi/l/trading-api-wrappers.svg)](https://opensource.org/licenses/MIT)\n[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdelta575%2Ftrading-api-wrappers.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdelta575%2Ftrading-api-wrappers?ref=badge_shield)\n\nThe MIT License\n\nCopyright © 2017\n[Felipe Aránguiz](mailto://faranguiz575@gmail.com) | [Sebastián Aránguiz](mailto://sarang575@gmail.com)\n\nSee [LICENSE](LICENSE)\n\n[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fdelta575%2Ftrading-api-wrappers.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fdelta575%2Ftrading-api-wrappers?ref=badge_large)\n\n## Donations\n\nBitcoin:\n\n    186kDw9LFcPvup17YSrWZbFqdZzELUFad3\n\nEther:\n\n    0xeF38fA6c0a37A1BdB60CADd7f6e71F351F6d2583\n',
    'author': 'Felipe Aranguiz',
    'author_email': 'faranguiz575@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/snake575/trading-bots',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
