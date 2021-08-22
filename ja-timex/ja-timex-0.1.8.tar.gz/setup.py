# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ja_timex', 'ja_timex.pattern']

package_data = \
{'': ['*'], 'ja_timex': ['dictionary/*']}

install_requires = \
['mojimoji>=0.0.11,<0.0.12', 'pendulum>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'ja-timex',
    'version': '0.1.8',
    'description': 'Analyze and parse natural language temporal expression from Japanese sentences',
    'long_description': '![](docs/docs/img/logo_title_wide.png)\n\n# ja-timex\n\n自然言語で書かれた時間情報表現を抽出/規格化するルールベースの解析器\n\n## 概要\n`ja-timex` は、現代日本語で書かれた自然文に含まれる時間情報表現を抽出し`TIMEX3`と呼ばれるアノテーション仕様に変換することで、プログラムが利用できるような形に規格化するルールベースの解析器です。\n\n以下の機能を持っています。\n\n- ルールベースによる日本語テキストからの日付や時刻、期間や頻度といった時間情報表現を抽出\n- アラビア数字/漢数字、西暦/和暦などの多彩なフォーマットに対応\n- 時間表現のdatetime/timedeltaオブジェクトへの変換サポート\n\n### 入力\n\n```python\nfrom ja_timex import TimexParser\n\ntimexes = TimexParser().parse("彼は2008年4月から週に3回ジョギングを1時間行ってきた")\n```\n\n### 出力\n\n```python\n[<TIMEX3 tid="t0" type="DATE" value="2008-04-XX" text="2008年4月">,\n <TIMEX3 tid="t1" type="SET" value="P1W" freq="3X" text="週に3回">,\n <TIMEX3 tid="t2" type="DURATION" value="PT1H" text="1時間">]\n```\n\n### datetime/timedeltaへの変換\n\n```python\n# <TIMEX3 tid="t0" type="DATE" value="2008-04-XX" text="2008年4月">\nIn []: timexes[0].to_datetime()\nOut[]: DateTime(2008, 4, 1, 0, 0, 0, tzinfo=Timezone(\'Asia/Tokyo\'))\n```\n\n\n```python\n# <TIMEX3 tid="t2" type="DURATION" value="PT1H" text="1時間">\nIn []: timexes[2].to_duration()\nOut[]: Duration(hours=1)\n```\n\n## インストール\n\n```\npip install ja-timex\n```\n\n## ドキュメント\n[ja\\-timex documentation](https://ja-timex.github.io/docs/)\n\n### 参考仕様\n本パッケージは、以下の論文で提案されている時間情報アノテーションの枠組みを元に作成しています。\n\n- [1] [小西光, 浅原正幸, & 前川喜久雄. (2013). 『現代日本語書き言葉均衡コーパス』 に対する時間情報アノテーション. 自然言語処理, 20(2), 201-221.](https://www.jstage.jst.go.jp/article/jnlp/20/2/20_201/_article/-char/ja/)\n- [2] [成澤克麻 (2014)「自然言語処理における数量表現の取り扱い」東北大学大学院 修士論文](http://www.cl.ecei.tohoku.ac.jp/publications/2015/mthesis2013_narisawa_submitted.pdf)\n',
    'author': 'Yuki Okuda',
    'author_email': 'y.okuda@dr-ubie.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yagays/ja-timex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
