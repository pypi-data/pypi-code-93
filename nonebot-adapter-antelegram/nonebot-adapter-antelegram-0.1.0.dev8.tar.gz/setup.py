# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot', 'nonebot.adapters.telegram']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.0,<0.19.0', 'nonebot2>=2.0.0a15,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-adapter-antelegram',
    'version': '0.1.0.dev8',
    'description': 'Another unofficial Telegram adapter for nonebot2',
    'long_description': '# nonebot-adapter-telegram\n（施工中）自己用的非官方nonebot2 telegram adapter，代码全靠糊  \n开发中代码没有经过清理和优化，不能与官方版本共存  \n当前仅支持有限类型的消息解析和发送（接受私聊/群聊文字/图片，发送私聊/群聊文字/图片/语音，入群事件）  \n需要公网ip或者frp  \n演示bot[@aya_od_bot](https://t.me/aya_od_bot)  \n## 使用方法\n如果要试毒的话  \n真的要的话  \n```shell\npip install nonebot-adapter-antelegram\n```\n## 上路\n一、 \n新建项目文件夹\n二、  \n在nonebot2的配置文件中配置以下选项  \n```shell\nhost=127.0.0.1 # 配置 NoneBot 监听的 IP / 主机名  \nport=xxxxx     # 配置 NoneBot 监听的端口  \nwebhook_host=your_domain # 配置telegram webhook域名，由于telegram要求webhook地址必须为https，我们需要在之后配置反向代理  \nbot_token=your_bot_token  #telegram bot token\n```\n三、\n将域名解析到本机，用你喜欢的方式配置反代将webhook域名的流量转发到nonebot2的监听端口  \n四、\n开始写机器人（摸鱼）\n\n## 最简单的例子\nbot.py\n```python\nimport nonebot\nfrom nonebot.adapters.telegram import Bot\n\nnonebot.init()\ndriver = nonebot.get_driver()\ndriver.register_adapter("your_bot_token", Bot) #your_bot_token替换为bot的token\nnonebot.load_plugin("plugins.echo")\n\nif __name__ == "__main__":\n    nonebot.run()   \n```\nplugins/echo.py\n```python\nfrom nonebot.plugin import on, on_command\nfrom nonebot.adapters.telegram import Bot, MessageEvent, Message, MessageSegment\nfrom nonebot.rule import to_me\n\necho = on_command("echo",to_me())\n\n@echo.handle()\nasync def echo_escape(bot: Bot, event: MessageEvent):\n    await bot.send(message=event.get_message(), event=event)\n\n#await bot.send(message="114514", event=event) #发送文字\n#await bot.send(message=MessageSegment.photo(pic_url)), event=event) #发送图片 支持file:///，base64://，file_id，url(由Telegram服务器下载)\n```\n运行机器人，向bot私聊发送/echo 123，bot会将消息原样重新发送\n\n\n',
    'author': 'ColdThunder11',
    'author_email': 'lslyj27761@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ColdThunder11/nonebot-adapter-telegram',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
