# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_epicfree']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.0,<0.19.0', 'nonebot2>=2.0.0-alpha.14,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-epicfree',
    'version': '0.1.1',
    'description': 'A Epic free game info plugin for Nonebot2',
    'long_description': '<h1 align="center">Nonebot Plugin EpicFree</h1></br>\n\n\n<p align="center">🤖 用于获取 Epic 限免游戏资讯的 Nonebot2 插件</p></br>\n\n\n<p align="center">\n  <a href="https://github.com/monsterxcn/nonebot_plugin_epicfree/actions">\n    <img src="https://img.shields.io/github/workflow/status/monsterxcn/Typecho-Theme-VOID/Build?style=flat-square" alt="actions">\n  </a>\n  <a href="https://raw.githubusercontent.com/monsterxcn/nonebot_plugin_epicfree/master/LICENSE">\n    <img src="https://img.shields.io/github/license/monsterxcn/nonebot_plugin_epicfree?style=flat-square" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot_plugin_epicfree">\n    <img src="https://img.shields.io/pypi/v/nonebot_plugin_epicfree?style=flat-square" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue?style=flat-square" alt="python"><br />\n</p></br>\n\n\n**安装方法**\n\n\n可以使用以下两命令快速安装，但请注意可能引起的依赖版本冲突。\n\n如果 `pip` 配置了 PyPI 镜像（推荐清华大学 PyPI 镜像），你可能无法及时检索到插件最新版本。\n\n\n``` zsh\nnb plugin install nonebot_plugin_epicfree\n# or\npip install --upgrade nonebot_plugin_epicfree\n```\n\n\n<details><summary> **关于依赖版本** </summary></br>\n\n\n以上述方式安装本插件时，可能由于版本差异引起报错，对于新手推荐在安装插件前先存留当前环境依赖版本，以便后续恢复：\n\n\n```bash\n# 备份当前的依赖版本\npip3 freeze > requirements.txt\n\n# 尝试安装 nonebot_plugin_epicfree\n\n# 安装备份的依赖版本\npip3 install -r requirements.txt\n```\n\n\n如果安装前未存留备份，可以在 **安装完本插件后**，使用 `pip3 install --upgrade nb-cli` 按最新版本 `nb-cli` 的依赖重新安装，实测不影响此插件使用。\n\n建议使用 **Python 虚拟环境**。\n\n\n</details>\n\n\n在 Nonebot2 入口文件（例如 `bot.py`）增加：\n\n\n``` python\nnonebot.load_plugin("nonebot_plugin_epicfree")\n```\n\n\n**指令详解**\n\n\n```python\n# nonebot_plugin_epicfree/nonebot_plugin_epicfree/__init__.py#L7\nmatcher = on_regex("((E|e)(P|p)(I|i)(C|c))?喜(加一|\\+1)")\n```\n\n\n基于正则匹配，所以，甚至 `EpIc喜+1` 这样的指令都可用！（\n\n如果你觉得不顺眼也可以自己参考 Nonebot2 文档修改下。\n\n\n**特别鸣谢**\n\n\n[@nonebot/nonebot2](https://github.com/nonebot/nonebot2/) | [@Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp) | [@DIYgod/RSSHub](https://github.com/DIYgod/RSSHub) | [@SD4RK/epicstore_api](https://github.com/SD4RK/epicstore_api)',
    'author': 'monsterxcn',
    'author_email': 'monsterxcn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monsterxcn/nonebot_plugin_epicfree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0',
}


setup(**setup_kwargs)
