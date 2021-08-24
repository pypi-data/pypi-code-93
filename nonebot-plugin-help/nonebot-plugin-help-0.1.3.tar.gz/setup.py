# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_help']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-cqhttp>=2.0.0a11.post2,<3.0.0',
 'nonebot2>=2.0.0-alpha.10,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-help',
    'version': '0.1.3',
    'description': 'A general help lister for nonebot2 plugins',
    'long_description': '# nonebot-plugin-help\nA general help plugin for nonebot2\n\n为nonebot2插件提供泛用的帮助列表\n\n## 开发者接入此插件列表方法\n\n使用python包形态的插件（已发布/自行开发皆可），并在插件包的__init__.py文件内增加如下代码：\n```python\n# 若此文本不存在，将显示包的__doc__\n__usage__ = \'您想在使用命令/help <your plugin package name>时提供的帮助文本\'\n\n# 您的插件版本号，将在/help list中显示\n__help__version__ = \'0.1.3\' \n\n# 此名称有助于美化您的插件在/help list中的显示\n# 但使用/help xxx查询插件用途时仍必须使用包名\n__help__plugin_name__ = "您的插件名称（有别于nonebot-plugin-xxx的包名）" \n```\n\n## 实际使用\n### 查看已加载插件列表\n指令：/help list\n\n返回示例：\n```\n@<user_who_send_command> 已加载插件：\ndice: XZhouQD\'s Roll 0.1.0\nnonebot_plugin_help: XZhouQD\'s Help Menu 0.1.0\nnonebot_plugin_apscheduler \nnonebot_plugin_status \n```\n\n### 查看已加载某一插件用途\n指令：/help <plugin_package_name>\n示例：\n```\n/help help\n\n@<user_who_send_command> 欢迎使用Nonebot 2 Help Plugin，请输入/help 获取使用方法\n```\n\n若插件未提供__usage__，则会显示__doc__，示例：\n```\n/help nonebot_plugin_status\n\n@<user_who_send_command>\n@Author         : yanyongyu\n@Date           : 2020-09-18 00:00:13\n@LastEditors    : yanyongyu\n@LastEditTime   : 2021-03-16 17:05:58\n@Description    : None\n@GitHub         : https://github.com/yanyongyu\n```',
    'author': 'XZhouQD',
    'author_email': 'X.Zhou.QD@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/XZhouQD/nonebot-plugin-help',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
