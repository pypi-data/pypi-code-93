# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ankicc']

package_data = \
{'': ['*']}

install_requires = \
['OpenCC>=1.1.1,<2.0.0', 'ankipandas>=0.3.10,<0.4.0']

entry_points = \
{'console_scripts': ['ankicc = ankicc.console:run']}

setup_kwargs = {
    'name': 'ankicc',
    'version': '0.2.2',
    'description': 'Convert all fields of Anki deck package (*.apkg) between traditional and simplified Chinese',
    'long_description': '# ankicc\n\n將 Anki deck package (*.apkg) 的所有欄位在繁體及簡體中文間進行相互轉換。\n\n## Installation 安裝\n\n```\npip install ankicc\n```\n\n## Usage 使用\n\n```\nusage: ankicc [-h] --apkg_path APKG_PATH [--workspace WORKSPACE] --output_path OUTPUT_PATH\n              [--convertor {t2jp.json,t2tw.json,hk2t.json,tw2s.json,hk2s.json,s2hk.json,tw2t.json,t2s.json,s2tw.json,s2twp.json,t2hk.json,s2t.json,jp2t.json,tw2sp.json}]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --apkg_path APKG_PATH\n  --workspace WORKSPACE\n  --output_path OUTPUT_PATH\n  --convertor {t2jp.json,t2tw.json,hk2t.json,tw2s.json,hk2s.json,s2hk.json,tw2t.json,t2s.json,s2tw.json,s2twp.json,t2hk.json,s2t.json,jp2t.json,tw2sp.json}\n```\n\n* apkg_path: 待轉換的 apkg 文件位置\n* workspace: ankicc 的工作目錄位置，預設為當前執行目錄，轉換過程中的文件都會保存在該執行目錄 (請留意：轉換後不會自動刪除)\n* output_path: 轉換後的輸出文件位置\n* convertor: OpenCC 的翻譯器設定，預設為簡體轉繁體 (s2t.json)，其他翻譯器設定請參考 [OpenCC #Configurations](https://github.com/BYVoid/OpenCC#configurations-%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)\n\n## Third Party Library 第三方庫\n\n* [OpenCC](https://github.com/BYVoid/OpenCC) Apache-2.0 License\n* [AnkiPandas](https://github.com/klieret/AnkiPandas) MIT License\n',
    'author': 'kaiiiz',
    'author_email': 'ukaizheng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
