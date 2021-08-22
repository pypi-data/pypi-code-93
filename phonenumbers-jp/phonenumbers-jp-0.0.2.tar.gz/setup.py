# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['phonenumbers_jp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'phonenumbers-jp',
    'version': '0.0.2',
    'description': 'Analyze Japanese domestic phone numbers',
    'long_description': '# phonenumbers-jp-py\n\n![Test](https://github.com/ciscorn/phonenumbers-jp-py/actions/workflows/test.yml/badge.svg?branch=main)\n[![codecov](https://codecov.io/gh/ciscorn/phonenumbers-jp-py/branch/main/graph/badge.svg)](https://codecov.io/gh/ciscorn/phonenumbers-jp-py)\n[![pypi package](https://img.shields.io/pypi/v/phonenumbers-jp?color=%2334D058&label=pypi%20package)](https://pypi.org/project/phonenumbers-jp)\n\nGet attribute information from Japanese domestic phone numbers.\n\n日本国内の電話番号から、種別や市外局番などの情報を取得します。\n\nLicense: MIT\n\n## Installation\n\n```bash\npip3 install phonenumbers-jp -U\n```\n\n## Examples\n\n```python\n>>> phonenumbers_jp.parse("0311111111")\nNumberInfo(parts=[\'03\', \'1111\', \'1111\'], type=\'固定\', subtype=None, message_area=NumberAndName(number=\'03\', name=\'東京\'), specified_carrier=None, callerid_delivery=None)\n\n>>> phonenumbers_jp.parse("0992000000")\nNumberInfo(parts=[\'099\', \'200\', \'0000\'], type=\'固定\', subtype=None, message_area=NumberAndName(number=\'099\', name=\'鹿児島\'), specified_carrier=None, callerid_delivery=None)\n\n>>> phonenumbers_jp.parse("1840992000000")\nNumberInfo(parts=[\'184\', \'099\', \'200\', \'0000\'], type=\'固定\', subtype=None, message_area=NumberAndName(number=\'099\', name=\'鹿児島\'), specified_carrier=None, callerid_delivery=\'withhold\')\n\n>>> phonenumbers_jp.parse("09011112222")\nNumberInfo(parts=[\'090\', \'1111\', \'2222\'], type=\'携帯\', subtype=None, message_area=None, specified_carrier=None, callerid_delivery=None)\n\n>>> phonenumbers_jp.parse("117")\nNumberInfo(parts=[\'117\'], type=\'特番\', subtype=\'時報\', message_area=None, specified_carrier=None, callerid_delivery=None)\n\n>>> phonenumbers_jp.parse("05012345678")\nNumberInfo(parts=[\'050\', \'1234\', \'5678\'], type=\'IP\', subtype=None, message_area=None, specified_carrier=None, callerid_delivery=None)\n\n>>> phonenumbers_jp.parse("00630111111111")\nNumberInfo(parts=[\'0063\', \'011\', \'111\', \'1111\'], type=\'固定\', subtype=None, message_area=NumberAndName(number=\'011\', name=\'札幌\'), specified_carrier=NumberAndName(number=\'0063\', name=\'ソフトバンク株式会社\'), callerid_delivery=None)\n\n>>> phonenumbers_jp.parse("0120444444")\nNumberInfo(parts=[\'0120\', \'444\', \'444\'], type=\'フリーダイヤル\', subtype=None, message_area=None, specified_carrier=None, callerid_delivery=None)\n```\n\n## API\n\n```python\nNumberTypes = Literal[\n    "特番", "固定", "携帯", "IP", "M2M", "国際電話", "国外",\n    "フリーダイヤル", "FMC", "ポケベル", "災害募金サービス", "ナビダイヤル"\n]\n\n@dataclass\nclass NumberAndName:\n    number: str\n    name: str\n\n@dataclass\nclass NumberInfo:\n    parts: List[str] = field(default_factory=list)  # 分解された電話番号\n    type: Optional[NumberTypes] = None  # 種別\n    subtype: Optional[str] = None  # 特番の内容\n    message_area: Optional[NumberAndName] = None  # メッセージエリア (市外局番)\n    specified_carrier: Optional[NumberAndName] = None  # 事業者指定番号\n    callerid_delivery: Optional[Literal["withhold", "provide"]] = None  # 非通知・通知\n\ndef parse(number: str) -> NumberInfo:\n    ...\n```\n',
    'author': 'Taku Fukada',
    'author_email': 'naninunenor@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ciscorn/phonenumbers-jp-py',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
