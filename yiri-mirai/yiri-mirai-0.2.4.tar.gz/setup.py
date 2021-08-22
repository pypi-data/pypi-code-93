# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mirai', 'mirai.adapters', 'mirai.models']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0',
 'httpx>=0.18.2,<0.19.0',
 'pydantic>=1.8.2,<2.0.0',
 'starlette>=0.14.2,<1.0',
 'websockets>=9.1,<10.0']

extras_require = \
{':python_version == "3.7"': ['typing-extensions>=3.10.0,<4.0.0'],
 'hypercorn': ['hypercorn>=0.11.2,<1.0'],
 'uvicorn': ['uvicorn[standard]>=0.14.0,<1.0']}

setup_kwargs = {
    'name': 'yiri-mirai',
    'version': '0.2.4',
    'description': '一个轻量级、低耦合的基于 mirai-api-http 的 Python SDK。',
    'long_description': "# YiriMirai\n\n[![Licence](https://img.shields.io/github/license/YiriMiraiProject/YiriMirai)](https://github.com/YiriMiraiProject/YiriMirai/blob/master/LICENSE)\n[![PyPI](https://img.shields.io/pypi/v/yiri-mirai)](https://pypi.org/project/yiri-mirai/)\n[![Python Version](https://img.shields.io/pypi/pyversions/yiri-mirai)](https://docs.python.org/zh-cn/3.7/)\n[![Document](https://img.shields.io/badge/document-vercel-brightgreen)](https://yiri-mirai.vercel.app)\n[![CodeFactor](https://www.codefactor.io/repository/github/yirimiraiproject/yirimirai/badge/dev)](https://www.codefactor.io/repository/github/yirimiraiproject/yirimirai/overview/dev)\n\n一个轻量级、低耦合度的基于 mirai-api-http 的 Python SDK。\n\n**本项目适用于 mirai-api-http 2.0 以上版本**。\n\n目前仍处于开发阶段，各种内容可能会有较大的变化。\n\n## 安装\n\n从 PyPI 安装：\n\n```shell\npip install yiri-mirai\n# 或者使用 poetry\npoetry add yiri-mirai\n```\n\n此外，你还可以克隆这个仓库到本地，然后使用 `poetry` 安装：\n\n```shell\ngit clone git@github.com:Wybxc/YiriMirai.git\ncd YiriMirai\npoetry install\n```\n\n## 使用\n\n```python\nfrom mirai import Mirai, FriendMessage, WebSocketAdapter\n\nif __name__ == '__main__':\n    bot = Mirai(12345678, adapter=WebSocketAdapter(\n        verify_key='your_verify_key', host='localhost', port=6090\n    ))\n\n    @bot.on(FriendMessage)\n    async def on_friend_message(event: FriendMessage):\n        if str(event.message_chain) == '你好':\n            await bot.send(event, 'Hello World!')\n\n    bot.run()\n```\n\n更多信息参看[文档](https://yiri-mirai.wybxc.cc/)或[文档镜像](https://yiri-mirai.vercel.app)。\n\n## 社区\n\nQQ 群：766952599（[链接](https://jq.qq.com/?_wv=1027&k=PXBOuBCI)）\n\nGithub Discussion（[链接](https://github.com/YiriMiraiProject/YiriMirai/discussions)）\n\nDiscord（[链接](https://discord.gg/RaXsHFC3PH)）\n\n## 开源协议\n\n由于 mirai 及 mirai-api-http 均采用了 AGPL-3.0 开源协议，本项目同样采用 AGPL-3.0 协议。\n\n请注意，AGPL-3.0 是传染性协议。如果你的项目引用了 YiriMirai，请在发布时公开源代码，并同样采用 AGPL-3.0 协议。\n",
    'author': '忘忧北萱草',
    'author_email': 'wybxc@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://yiri-mirai.vercel.app',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
