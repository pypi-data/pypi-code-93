# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_cocdicer']

package_data = \
{'': ['*']}

install_requires = \
['nonebot2>=2.0.0-alpha.10,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-cocdicer',
    'version': '0.2.5',
    'description': 'A COC dice plugin for Nonebot2',
    'long_description': '<div align="center">\n\n# NoneBot Plugin COC-Dicer\n\nCOC骰子娘插件 For Nonebot2\n\n</div>\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/abrahum/nonebot-plugin-cocdicer/master/LICENSE">\n    <img src="https://img.shields.io/github/license/abrahum/nonebot_plugin_cocdicer.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-cocdicer">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-cocdicer.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">\n</p>\n\n## 使用方法\n\n``` zsh\nnb plugin install nonebot-plugin-cocdicer // or\npip install --upgrade nonebot-plugin-cocdicer\n```\n在 Nonebot2 入口文件（例如 bot.py ）增加：\n``` python\nnonebot.load_plugin("nonebot_plugin_cocdicer")\n```\n启动机器人后，输入 `.help` 获取帮助信息。\n\n遇到任何问题，欢迎开 Issue ~\n\n## 骰娘技能\n\n- Done or Will be done soon\n\n    - [x] .r    投掷指令\n    - [x] .sc   san check\n    - [x] .st   射击命中判定\n    - [x] .ti   临时疯狂症状\n    - [x] .li   总结疯狂症状\n    - [x] .coc  coc角色作成\n    - [x] .help 帮助信息\n    - [x] .en   技能成长\n    - [x] .set  角色卡设定\n    - [x] .show 角色卡查询\n    - [x] .sa   快速检定指令\n    - [x] .del  删除信息\n\n- To Do\n\n    - [ ] .kp   KP模式\n    - [ ] .pc   多角色卡管理、转让\n    - [ ] .rule 规则速查（优先级较低）\n    - [ ] set 技能值设定、sa 组合检定\n    - [ ] en 使用保存的技能数值\n\n## 指令详解\n\n```\n.r[dah#bp] a_number [+/-]ex_number\n```\n- d：骰子设定指令，标准格式为 xdy ， x 为骰子数量 y 为骰子面数， x 为1时可以省略， y 为100时可以省略；\n- a：检定指令，根据后续 a_number 设定数值检定，注意 a 必须位于 a_number 之前，且 a_number 前需使用空格隔开；\n- h：暗骰指令，骰子结构将会私聊发送给该指令者；（没测试过非好友，可以的话先加好友吧）\n- #：多轮投掷指令， # 后接数字即可设定多轮投掷，注意 # 后数字无需空格隔开；\n- b：奖励骰指令，仅对 D100 有效，每个 b 表示一个奖励骰；\n- p：惩罚骰指令，同奖励骰；\n- +/-：附加计算指令，目前仅支持数字，同样无需空格隔开。\n\n> 举几个栗子：\n> - `.r#2bba 70`：两次投掷 1D100 ，附加两个奖励骰，判定值为70；\n> - `.rah`：D100暗骰，由于没有 a_number 参数，判定将被忽略；\n> - `.ra2d8+10 70`：2D8+10，由于非D100，判定将被忽略。\n\n以上指令理论上均可随意变更顺序并嵌套使用，如果不能，就是出bug了_(:3」∠)_\n\n```\n.sc success/failure [san_number]\n```\n- success：判定成功降低 san 值，支持 x 或 xdy 语法（ x 与 y 为数字）；\n- failure：判定失败降低 san 值，支持语法如上；\n- san_number：当前 san 值，缺省 san_number 将会自动使用保存的人物卡数据。\n\n```\n.en skill_level\n```\n\n- skill_level：需要成长的技能当前等级。\n\n```\n.coc [age]\n```\n- age：调查员年龄，缺省 age 默认年龄 20\n\n> 交互式调查员创建功能计划中\n\n```\n.set [attr_name] [attr_num]\n```\n- attr_name：属性名称，例:name、名字、str、力量\n- attr_num：属性值\n- **可以单独输入 .set 指令，骰娘将自动读取最近一次 coc 指令结果进行保存**\n\n| 属性名称 | 缩写  |\n| :------: | :---: |\n|   名称   | name  |\n|   年龄   |  age  |\n|   力量   |  str  |\n|   体质   |  con  |\n|   体型   |  siz  |\n|   敏捷   |  dex  |\n|   外貌   |  app  |\n|   智力   |  int  |\n|   意志   |  pow  |\n|   教育   |  edu  |\n|   幸运   |  luc  |\n|   理智   |  san  |\n\n```\n.show[s] [@xxx]\n```\n- .shows 查看技能指令\n- 查看指定调查员保存的人物卡，缺省 at 则查看自身人物卡\n\n```\n.sa [attr_name]\n```\n- attr_name：属性名称，例:name、名字、str、力量\n\n```\n.del [c|card|xxx]\n```\n\n- c：清空暂存的人物卡\n- card：删除使用中的人物卡(慎用)\n- xxx：其他任意技能名\n- 以上指令支持多个混合使用，多个参数使用空格隔开\n\n## Change Log\n\n### 0.2.5\n\n- 暗投错误的使用了 get_session_id，已修复使用 get_user_id。\n\n### 0.2.4\n\n- 临时紧急修复 sc 指令逻辑问题（竟然还有人用这个插件）\n- 不保证修完没 bug\n- 用了怎么也不 star （小声bb）\n\n### 0.2.2\n\n- 增加技能系统\n- 增加 del 指令(总感觉 del 还有大 bug ···)\n\n### 0.2.1\n\n- 增加 set 、 show 、 sa 指令\n- 帮助信息重构\n\n## 特别鸣谢\n\n[nonebot/nonebot2](https://github.com/nonebot/nonebot2/)：简单好用，扩展性极强的 Bot 框架\n\n[Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)：更新迭代快如疯狗的 [OneBot](https://github.com/howmanybots/onebot/blob/master/README.md) Golang 原生实现\n',
    'author': 'abrahumlink',
    'author_email': '307887491@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abrahum/nonebot_plugin_cocdicer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
