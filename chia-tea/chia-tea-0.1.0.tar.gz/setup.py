# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chia_tea',
 'chia_tea.chia_watchdog',
 'chia_tea.chia_watchdog.api',
 'chia_tea.chia_watchdog.logfile',
 'chia_tea.config',
 'chia_tea.copy_plots',
 'chia_tea.discord',
 'chia_tea.discord.notifications',
 'chia_tea.monitoring',
 'chia_tea.protobuf',
 'chia_tea.protobuf.data_collection',
 'chia_tea.protobuf.generated',
 'chia_tea.protobuf.to_sqlite',
 'chia_tea.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'aiohttp==3.7.4',
 'chia-blockchain>=1.2.3,<2.0.0',
 'concurrent-log-handler>=0.9.19,<0.10.0',
 'discord>=1.7.3,<2.0.0',
 'grpcio>=1.39.0,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'py-cpuinfo>=8.0.0,<9.0.0',
 'sortedcontainers==2.3.0']

extras_require = \
{':sys_platform == "win32"': ['pywin32==225']}

setup_kwargs = {
    'name': 'chia-tea',
    'version': '0.1.0',
    'description': 'A library dedicated to chia-blockchain farmer.',
    'long_description': '# Chia Tea 🌱🍵\n\nChia Tea is a tools and utility library for the Chia Cryptocurrency.\nWe are building tools in this library to serve our own needs and share our work openly with others.\nFeel free to use them and make your life easier 💚\n\n# Table of Contents\n\n- [Intro and FAQ](docs/faq.md)\n- [Quick-Start](docs/quick_start.md)\n- [Architecture Summary](docs/architecture_summary.md)\n- [Structure of this repository](#structure-of-this-repository)\n- [Feature Overview](#feature-overview)\n  - [Copy Tool](#copy-tool)\n  - [Monitoring](#monitoring)\n  - [Discord Bot](#discord-bot)\n- [Contributions](#contributions)\n- [About Us](#about-us)\n- [✊ Support Us ✊](#support-us)\n\n## Structure of this repository\n\n![Chia-Tea Infrastructure](docs/Chia_Infrastructure.png?raw=true)\n\n## Feature Overview\n\n### Copy Tool\n\nCopy is a tool to copy your chia files to a different location. It can be faster to plot to a temporary storage space and then move the plots to your harvester afterwards to not block the plotting queue. We manage this process through our copy cli tool. It incorporates the following features:\n\n- Selects a drive with sufficient space from multiple disks specified\n- Checks drive space regularly\n- Takes plots which are being copied already into account\n- Uses the drive with the fewest copy processes\n- Logs transfer times\n\n### Monitoring\n\nThe monitoring tracks everything relevant to a Chia farm, including harvesters, farmers, plotters, etc. It consists of a server and multiple clients. The server is run on only one machine. It stores all the monitoring data in a sqlite database. The clients are the data collectors and are typically run on plotters, harvesters, farmers, etc. Simply start them on the same machine and they will collect data automatically. You can run both server and client on the same machine if you have a single machine setup.\n\n### Discord Bot\n\nThe discord module is a bot watching a farm and reports major incidents. Internally the bot keeps an eye on the sqlite database thus a running monitoring server is required. Besides notifications the bot also provides commands to interact with the chia farm.\n\n<a name="about-us"></a>\n\n## About Us\n\nWe are a small group of professional engineers and software developers doing Chia for fun. Join our discord server: https://discord.gg/azNjcVPYnY for questions, tips and tricks or just come over for a nice warm cup of your favourite tea.\n\n<a name="security"></a>\n\n## Contributions\n\nDue to security concerns, we only accept small PR\'s with limited complexity to our codebase.\n\n<a name="support-us"></a>\n\n## ✊ Support Us ✊\n\nThe more you support us, the easier we can make your life as a Chia farmer. Every little bit helps and motivates us to do more.\n\n| Currency | Address                                                                                                 |\n| -------- | ------------------------------------------------------------------------------------------------------- |\n| Chia     | xch13yrhjp0zleepsafjh8syh0jyakjgat9fzlut575lq0z5jywmydeqy05awj                                          |\n| BTC      | bc1qwjyh0fu708zv0yqdmp098tq465qy64jpmqpj4y                                                              |\n| ETH      | 0xeeaA95F8816208b4bb8D070ab571941843246029                                                              |\n| ADA      | addr1qxc2amr663yfh9z4cdk8d6hkv9apvm35dm5lkgjdlu6ffkfggrvustlynuxzqmswee4mvd6cfeu66hq788rmgts2uggq7qtuqh |\n',
    'author': 'Tea n Tech',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.youtube.com/channel/UCba194Pls_bHSqWoWMGoyzA',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
