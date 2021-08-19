# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pybitflyer2']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'websocket-client>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'pybitflyer2',
    'version': '0.0.3',
    'description': 'pybitflyer2 is a wrapper interface of Bitflyer lightning API',
    'long_description': '# pybitflyer2 - a wrapper interface of Bitflyer lightning API\n\ninspired by Ruby bitflyer gem https://github.com/unhappychoice/bitflyer\n\n## Usage\n\nSee https://lightning.bitflyer.jp/docs for details.\n\n## Requirements\n\n- Python 3\n\n## The Installation\n\nFrom Pypi with the Python package manager:\n\n```sh\npip install pybitflyer2\n```\n\n## Examples\n\n### HTTP API\n\nSee [http_public.py](https://github.com/fkshom/pybitflyer2/blob/master/src/pybitflyer2/http_public.py) / [http_private.rb](https://github.com/fkshom/pybitflyer2/blob/master/src/pybitflyer2/http_private.py) for method definition.\n\n```py\nfrom pybitflyer2 import Bitflyer\npublic_client = Bitflyer.http_public_client()\nprint(public_client.ticker(product_code=\'BTC_JPY\'))\n\nprivate_client = BitFlyer.http_private_client(\'YOUR_API_KEY\', \'YOUR_API_SECRET\')\nprivate_client.send_child_order(\n    product_code=\'BTC_JPY\',\n    child_order_type=\'LIMIT\',\n    side=\'BUY\',\n    price=30_000,\n    size=0.1,\n    minute_to_expire=10000,\n    time_in_force=\'GTC\',\n)\n#=> { "child_order_acceptance_id": "JRF20150707-050237-639234" }\n\nprivate_client.cancel_child_order(\n  "product_code": "BTC_JPY",\n  "child_order_acceptance_id": "JRF20150707-033333-099999"\n)\n#=> None\n```\n\n### Realtime API\n\n#### Public events\n\nChannel name format is like `{event_name}_{product_code}`. You can set handler to get realtime events.\n\n{event_name} and {product_code} is defined at [realtimeclient.py](https://github.com/fkshom/pybitflyer2/blob/master/src/bitflyer2/realtimeclient.py).\n\n#### Private events\n\nTo subscribe to the private child_order_events and parent_order_events, pass your API key and secret when creating the realtime_client.\n\n####\nThe Realtime Client automatically tries to reconnect when a connection is lost, and provides a variety of event-based notification.\n\n```py\nimport time\nfrom pybitflyer2 import Bitflyer\n\ndef on_ticker_received(ticker):\n    print(ticker)\n\ndef on_open():\n    print(\'opened\')\n\ndef on_error(err):\n    print(err)\n\ndef on_message(msg):\n    print(msg)\n\ndef on_close():\n    print(\'closed\')\n\nclient = Bitflyer.realtime_client()\nclient.subscribe(channel=\'lightning_ticker_BTC_JPY\', handler=on_ticker_received)\nclient.subscribe(channel=\'lightning_ticker_ETH_JPY\', handler=on_ticker_received)\nclient.on(\'open\', handler=on_open)\nclient.on(\'error\', handler=on_error)\nclient.on(\'message\', handler=on_message)\nclient.on(\'close\', handler=on_close)\nclient.start()\n\nwhile True:\n    time.sleep(1)\n```\n\n```json\n# lightning_ticker_BTC_JPY\n{\n      "product_code": "BTC_JPY",\n      "timestamp": "2019-04-11T05:14:12.3739915Z",\n      "state": "RUNNING",\n      "tick_id": 25965446,\n      "best_bid": 580006,\n      "best_ask": 580771,\n      "best_bid_size": 2.00000013,\n      "best_ask_size": 0.4,\n      "total_bid_depth": 1581.64414981,\n      "total_ask_depth": 1415.32079982,\n      "market_bid_size": 0,\n      "market_ask_size": 0,\n      "ltp": 580790,\n      "volume": 6703.96837634,\n      "volume_by_product": 6703.96837634\n}\n```\n\n```py\nimport time\nfrom pybitflyer2 import Bitflyer\n\ndef on_ticker_received(ticker):\n    print(ticker)\n\ndef on_private_event_received(event):\n    print(event)\n\ndef on_open():\n    print(\'opened\')\n\ndef on_error(err):\n    print(err)\n\ndef on_message(msg):\n    print(msg)\n\ndef on_close():\n    print(\'closed\')\n\nclient = Bitflyer.realtime_client(\'YOUR_API_KEY\', \'YOUR_API_SECRET\')\nclient.subscribe(channel=\'lightning_ticker_BTC_JPY\', handler=on_ticker_received)\nclient.subscribe(channel=\'lightning_ticker_ETH_JPY\', handler=on_ticker_received)\nclient.subscribe(channel=\'child_order_events\', handler=on_private_event_received)\nclient.on(\'open\', handler=on_open)\nclient.on(\'error\', handler=on_error)\nclient.on(\'message\', handler=on_message)\nclient.on(\'close\', handler=on_close)\n\nwhile True:\n    time.sleep(1)\n```\n\n```json\n# child_order_events\n[\n    {\n        "product_code": "BTC_JPY",\n        "child_order_id": "JOR20150101-070921-038077",\n        "child_order_acceptance_id": "JRF20150101-070921-194057",\n        "event_date": "2015-01-01T07:09:21.9301772Z",\n        "event_type": "ORDER",\n        "child_order_type": "LIMIT",\n        "side": "SELL",\n        "price": 500000,\n        "size": 0.12,\n        "expire_date": "2015-01-01T07:10:21"\n    }\n]\n```\n\n## Contributing\n\nBug reports and pull requests are welcome on GitHub at https://github.com/fkshom/pybitflyer2. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the Contributor Covenant code of conduct.\n\n## License\n\nThe gem is available as open source under the terms of the MIT License.\n',
    'author': 'Shoma FUKUDA',
    'author_email': 'fkshom+pypi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fkshom/pybitflyer2',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
