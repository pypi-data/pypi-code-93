# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nautobot_chatops',
 'nautobot_chatops.api',
 'nautobot_chatops.api.views',
 'nautobot_chatops.dispatchers',
 'nautobot_chatops.management.commands',
 'nautobot_chatops.migrations',
 'nautobot_chatops.tests',
 'nautobot_chatops.tests.workers',
 'nautobot_chatops.workers']

package_data = \
{'': ['*'], 'nautobot_chatops': ['static/nautobot/*', 'templates/nautobot/*']}

install_requires = \
['PyJWT>=2.1.0,<3.0.0',
 'nautobot',
 'nautobot-capacity-metrics',
 'slack-sdk>=3.4.2,<4.0.0',
 'texttable>=1.6.2,<2.0.0',
 'webexteamssdk>=1.3,<2.0']

entry_points = \
{'nautobot.workers': ['clear = nautobot_chatops.workers.clear:clear',
                      'nautobot = nautobot_chatops.workers.nautobot:nautobot']}

setup_kwargs = {
    'name': 'nautobot-chatops',
    'version': '1.5.0',
    'description': 'A plugin providing chatbot capabilities for Nautobot',
    'long_description': "# nautobot-chatops\n\nA multi-platform ChatOps bot plugin for [Nautobot](https://github.com/nautobot/nautobot).\n\n- Support for multiple chat platforms (currently Slack, Microsoft Teams, and WebEx)\n- Write a command once and run it on every supported platform, including rich content formatting\n- Extensible - other Nautobot plugins can provide additional commands which will be dynamically discovered.\n- Automatic generation of basic help menus (accessed via `help`, `/command help`, or `/command sub-command help`)\n- Metrics of command usage via the `nautobot_capacity_metrics` plugin.\n\n## Documentation\n\n- [Installation Guide](docs/chat_setup/chat_setup.md)\n- [Design](docs/design.md)\n- [Contributing](docs/contributing.md)\n- [FAQ](docs/FAQ.md)\n\n## Contributing\n\nThank you for your interest in helping to improve Nautobot!\nRefer to the [contributing guidelines](docs/contributing.md) for details.\n\n## Try it Out\n\nInterested to see Nautobot ChatOps in action?  It's currently setup on the [Demo Instance](https://demo.nautobot.com/) and integrated into [NTC Slack](slack.networktocode.com).  You can sign up for that Slack workspace and join the `#nautobot-chat` channel to understand what this bot can do and try it for yourself.  You can try these exact chat commands and many more:\n\n\n### Command: `/nautobot`\n\n![image](https://user-images.githubusercontent.com/6332586/118281576-5db4e980-b49b-11eb-8574-1332ed4b9757.png)\n\n### Command: `/nautobot get-devices`\n\n![image](https://user-images.githubusercontent.com/6332586/118281772-95239600-b49b-11eb-9c79-e2040dc4a982.png)\n\n\n### Command: `/nautobot get-interface-connections`\n\n\n![image](https://user-images.githubusercontent.com/6332586/118281976-ca2fe880-b49b-11eb-87ad-2a41eaa168ed.png)\n\n\n## Questions\n\nFor any questions or comments, please check the [FAQ](docs/FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #nautobot).\nSign up [here](http://slack.networktocode.com/)\n",
    'author': 'Network to Code, LLC',
    'author_email': 'opensource@networktocode.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nautobot/nautobot-plugin-chatops',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
