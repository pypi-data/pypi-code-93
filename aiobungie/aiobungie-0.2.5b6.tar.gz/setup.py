# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiobungie', 'aiobungie.crate', 'aiobungie.ext', 'aiobungie.internal']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.7.4.post0', 'attrs==21.2.0', 'python-dateutil==2.8.2']

setup_kwargs = {
    'name': 'aiobungie',
    'version': '0.2.5b6',
    'description': 'A small async api wrapper for the bungie api',
    'long_description': '<div align="center">\n    <h1>aiobungie</h1>\n    <p>An asynchronous statically typed API wrapper for the Bungie API written in Python.</p>\n    <a href="https://codeclimate.com/github/nxtlo/aiobungie/maintainability">\n    <img src="https://api.codeclimate.com/v1/badges/09e71a0374875d4594f4/maintainability"/>\n    </a>\n    <a href="https://github.com/nxtlo/aiobungie/issues">\n    <img src="https://img.shields.io/github/issues/nxtlo/aiobungie"/>\n    </a>\n    <a href="http://python.org">\n    <img src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10dev-blue"/>\n    </a>\n    <a href="https://pypi.org/project/aiobungie/">\n    <img src="https://img.shields.io/pypi/v/aiobungie?color=green"/>\n    </a>\n    <a href="https://github.com/nxtlo/aiobungie/blob/master/LICENSE">\n    <img src="https://img.shields.io/pypi/l/aiobungie"/>\n    </a>\n    <a href="https://www.codefactor.io/repository/github/nxtlo/aiobungie/">\n    <img src="https://www.codefactor.io/repository/github/nxtlo/aiobungie/badge">\n    </a>\n    <a href="https://github.com/nxtlo/aiobungie/actions/workflows/ci.yml">\n    <img src="https://github.com/nxtlo/aiobungie/actions/workflows/ci.yml/badge.svg?branch=master">\n    </a>\n    <a href="https://codeclimate.com/github/nxtlo/aiobungie/test_coverage"><img src="https://api.codeclimate.com/v1/badges/09e71a0374875d4594f4/test_coverage" /></a>\n\n</div>\n\n# Installing\n\n_IT IS recommended_ to use the latest release from master\nsince `0.2.4` is missing features from `0.2.5`.\n\nTheoretically you probably will encounter breaking changes every `0.2.5x` release.\n\nPyPI stable release.\n\n```sh\n$ pip install aiobungie\n```\n\nFrom master __Recommended Currently__.\n\n```sh\n$ pip install git+https://github.com/nxtlo/aiobungie\n```\n\n## Quick Example\n\nSee [Examples for more.](https://github.com/nxtlo/aiobungie/tree/master/examples)\n\n```python\nimport aiobungie\nfrom aiobungie import crate\n\n# crates in aiobungie are implementations\n# of Bungie\'s objects to provide\n# more functionality.\n\nclient = aiobungie.Client(key=\'YOUR_API_KEY\')\n\nasync def main() -> None:\n\n    # fetch a clan\n    clan: crate.Clan = await client.fetch_clan("Nuanceㅤ")\n    print(clan.name, clan.id, clan.owner.name, clan.owner.id, ...)\n\n    # fetch a member from the clan.\n    member: crate.ClanMember = await clan.fetch_member("Fate怒")\n    print(member.name, member.id, member.type, ...)\n\n    # fetch the clan members and return only steam players\n    members = await clan.fetch_members(aiobungie.MembershipType.STEAM)\n    for member in members:\n        if member.name == "Fate怒" or member.id == 4611686018484639825:\n            print(...)\n        else:\n            print(member.name, member.id, member.type)\n\n    # fetch my profile.\n    profile: crate.Profile = await client.fetch_profile(member.id, member.type)\n    print(profile.name, profile.id, profile.type, ...)\n\n    # You can fetch a character in two ways.\n    # Whether from the player\'s profile or\n    # using `fetch_character()` method.\n\n    # The profile way.\n    warlock: crate.Character = await profile.warlock()\n    print(warlock.light, warlock.id, warlock.gender, warlock.race, ...)\n\n    # the fetch_character() way using the profile attrs.\n    character: crate.Character = await client.fetch_character(profile.id, profile.type, profile.warlock_id)\n    print(character.light, character.id, character.gender, character.race, ...)\n```\n\n### Requirements\n* Python >=3.8 ,<=3.12\n* aiohttp\n* attrs.\n\n### Optional Requirements for speedups.\n* aiodns\n* cchardet\n* uvloop\n\n## Contributing\nSee the [manual](https://github.com/nxtlo/aiobungie/blob/master/CONTRIBUTING.md)\n\n### Getting Help\n* Discord: `Fate 怒#0008` | `350750086357057537`\n* Docs: [Here](https://nxtlo.github.io/aiobungie/).\n',
    'author': 'nxtlo',
    'author_email': 'dhmony-99@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nxtlo/aiobungie',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
