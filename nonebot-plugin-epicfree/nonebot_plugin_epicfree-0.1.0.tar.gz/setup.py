# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_epicfree']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.17.0,<0.18.0', 'nonebot2>=2.0.0.a1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-epicfree',
    'version': '0.1.0',
    'description': 'A Epic free game info plugin for Nonebot2',
    'long_description': '<h1 align="center">Nonebot Plugin EpicFree</h1>\n\n<div align="center">\n\n🤖 用于获取 Epic 限免游戏资讯的 Nonebot2 插件\n\n</div></br>\n\n\n<p align="center">\n  <a href="https://github.com/monsterxcn/nonebot_plugin_epicfree/actions">\n    <img src="https://img.shields.io/github/workflow/status/monsterxcn/Typecho-Theme-VOID/Build?style=flat-square" alt="actions">\n  </a>\n  <a href="https://raw.githubusercontent.com/monsterxcn/nonebot_plugin_epicfree/master/LICENSE">\n    <img src="https://img.shields.io/github/license/monsterxcn/nonebot_plugin_epicfree?style=flat-square" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot_plugin_epicfree">\n    <img src="https://img.shields.io/pypi/v/nonebot_plugin_epicfree?style=flat-square" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.0+-blue?style=flat-square" alt="python"><br />\n</p></br>\n\n\n**安装方法**\n\n\n``` zsh\nnb plugin install nonebot_plugin_epicfree\n# or\npip install --upgrade nonebot_plugin_epicfree\n```\n\n\n在 Nonebot2 入口文件（例如 `bot.py`）增加：\n\n\n``` python\nnonebot.load_plugin("nonebot_plugin_epicfree")\n```\n\n\n**指令详解**\n\n\n```python\n# nonebot_plugin_epicfree/nonebot_plugin_epicfree/__init__.py#L7\nmatcher = on_regex("((E|e)(P|p)(I|i)(C|c))?喜(加一|\\+1)")\n```\n\n\n基于正则匹配，所以，甚至 `EpIc喜+1` 这样的指令都可用！（\n\n如果你觉得不顺眼也可以自己参考 Nonebot2 文档修改下。\n\n\n**特别鸣谢**\n\n[@nonebot/nonebot2](https://github.com/nonebot/nonebot2/) | [@Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp) | [@DIYgod/RSSHub](https://github.com/DIYgod/RSSHub) | [@SD4RK/epicstore_api](https://github.com/SD4RK/epicstore_api)',
    'author': 'monsterxcn',
    'author_email': 'monsterxcn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monsterxcn/nonebot_plugin_epicfree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
