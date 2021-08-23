# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cay']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['cay = cay.cli:cli']}

setup_kwargs = {
    'name': 'cay',
    'version': '0.1.4',
    'description': 'Simple calculator implemented in Python',
    'long_description': '#+author: conao3\n#+date: <2020-03-20 Fri>\n\n[[https://github.com/conao3/cay][https://raw.githubusercontent.com/conao3/files/master/blob/headers/png/cay.png]]\n[[https://github.com/conao3/cay/blob/master/LICENSE][https://img.shields.io/github/license/conao3/cay.svg?style=flat-square]]\n[[https://github.com/conao3/cay/releases][https://img.shields.io/github/tag/conao3/cay.svg?style=flat-square]]\n[[https://github.com/conao3/cay/actions][https://img.shields.io/badge/patreon-become%20a%20patron-orange.svg?logo=patreon&style=flat-square]]\n[[https://twitter.com/conao_3][https://img.shields.io/badge/twitter-@conao__3-blue.svg?logo=twitter&style=flat-square]]\n[[https://conao3-support.slack.com/join/shared_invite/enQtNjUzMDMxODcyMjE1LWUwMjhiNTU3Yjk3ODIwNzAxMTgwOTkxNmJiN2M4OTZkMWY0NjI4ZTg4MTVlNzcwNDY2ZjVjYmRiZmJjZDU4MDE][https://img.shields.io/badge/chat-on_slack-blue.svg?logo=slack&style=flat-square]]\n\n* Table of Contents\n- [[#description][Description]]\n- [[#install][Install]]\n- [[#usage][Usage]]\n- [[#information][Information]]\n  - [[#community][Community]]\n  - [[#contribution][Contribution]]\n  - [[#license][License]]\n  - [[#author][Author]]\n\n* Description\nSimple calculator inplemented in Python.\n\n* Install\n\n* Usage\n\n* Information\n** Community\nAll feedback and suggestions are welcome!\n\nYou can use github issues, but you can also use [[https://conao3-support.slack.com/join/shared_invite/enQtNjUzMDMxODcyMjE1LWUwMjhiNTU3Yjk3ODIwNzAxMTgwOTkxNmJiN2M4OTZkMWY0NjI4ZTg4MTVlNzcwNDY2ZjVjYmRiZmJjZDU4MDE][Slack]]\nif you want a more casual conversation.\n\n** Contribution\nWe welcome PR!\n\n** License\n#+begin_example\n  MIT License\n  Copyright (c) Naoya Yamashita - https://conao3.com\n  https://github.com/conao3/cay/blob/master/LICENSE\n#+end_example\n\n** Author\n- Naoya Yamashita ([[https://github.com/conao3][conao3]])\n',
    'author': 'Naoya Yamashita',
    'author_email': 'conao3@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/conao3/cay',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
