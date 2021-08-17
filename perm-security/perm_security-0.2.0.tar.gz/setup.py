# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['perm_security',
 'perm_security.MemberAdapter',
 'perm_security.Permission',
 'perm_security.TokenStrategy',
 'perm_security.TokenStrategy.TokenHandlerStrategy',
 'perm_security.converters']

package_data = \
{'': ['*']}

install_requires = \
['APScheduler>=3.7.0,<4.0.0',
 'discord>=1.7.3,<2.0.0',
 'perm-banana>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'perm-security',
    'version': '0.2.0',
    'description': "A package to bridge the gap between Discord's API and Perm-Banana",
    'long_description': '\n# Perm-Security\n\n#### A package to enable the integration between Discord\'s API and Perm-Banana\n\n#### Features\n- Permission classes for converting Discord\'s Permissions to Perm-Banana\n- Member Adapters to enable Perm-Banana\'s extended functionality\n- The ability to create Tokens\n- A TokenStrategy for handling Permissions with Discord\'s API\n\n#### How to use it?\n\n```python\nfrom discord import Member\nfrom discord.ext.commands import Cog, Greedy, Context, command\n\nfrom perm_security.converters import PermissionChannelConverter\nfrom perm_security.MemberAdapter import MemberChannelAdapter\nfrom perm_security.TokenStrategy import BasicTokenStrategy\nfrom perm_security.TokenStrategy.TokenHandlerStrategy import BasicTokenHandlerStrategy\n\nclass Security(Cog):\n    def __init__(self, bot):\n        self.bot = bot\n        self.token_strategy = BasicTokenStrategy(BasicTokenHandlerStrategy(bot.scheduler))\n\n    @command(name="generate_toke")\n    async def generate_token(\n        self,\n        ctx: Context,\n        permissions: PermissionChannelConverter,\n        members: Greedy[Member],\n        uses: int = 1\n        duration: float = 60.0\n    ):\n        author = MemberChannelAdapter(ctx.author, ctx.channel)\n        await self.token_strategy.generate_token(author, permissions, members, uses, duration)\n```\n',
    'author': 'TheJoeSmo',
    'author_email': 'joesmo.joesmo12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TheJoeSmo/perm-security',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
