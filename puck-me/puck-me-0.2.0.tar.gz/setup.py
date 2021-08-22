# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['puck_me',
 'puck_me.game',
 'puck_me.goalie',
 'puck_me.lib',
 'puck_me.player',
 'puck_me.skater']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'html5lib>=1.1,<2.0',
 'lxml>=4.6.3,<5.0.0',
 'pandas>=1.3.1,<2.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'puck-me',
    'version': '0.2.0',
    'description': 'Puck Me is a python package for scraping NHL stats from the internet.',
    'long_description': '# Puck Me\n\nPuck Me is a python package for scraping NHL stats from the internet.\n\n## Basic Examples\n\n##### Print skater\'s names:\n\n```\nfrom puck_me.skater.skaters import Skaters\n\nall_skaters = Skaters.all_skaters("2009")\n\n# Print the name of the first three skaters\nfor skater in all_skaters[:3]:\n    print(skater.name)\n```\n\nOutput:\n\n```\n>>> Justin Abdelkader\n>>> Craig Adams\n>>> Maxim Afinogenov\n```\n\n##### Player Basic Stats:\n\n```\nfrom puck_me.skater.skaters import Skaters\n\nall_skaters = Skaters.all_skaters("2009")\n\nfor skater in all_skaters[:3]:\n    name = skater.name\n    games_played = skater.games_played()\n    points = skater.points()\n    print(f"{skater.name} played {games_played} games and scored {points} points.")\n```\n\nOutput:\n\n```\n>>> Justin Abdelkader played 2 games and scored 0 points.\n>>> Craig Adams played 45 games and scored 7 points.\n>>> Maxim Afinogenov played 48 games and scored 20 points.\n```\n\n##### Player Split Stats:\n\n```\nfrom puck_me.skater.skater import SplitType\nfrom puck_me.skater.skaters import Skaters\n\nall_skaters = Skaters.all_skaters("2009")\n\nfor skater in all_skaters[:3]:\n    name = skater.name\n    for arena_split in skater.splits(SplitType.ARENA):\n        value = arena_split.value\n        points = arena_split.points\n        print(f"At arena \'{value}\' {name} scored {points} points.")\n```\n\nOutput:\n\n```\n>>> At arena \'Home\' Justin Abdelkader scored 0 points.\n>>> At arena \'Road\' Justin Abdelkader scored 0 points.\n>>> At arena \'Home\' Craig Adams scored 3 points.\n>>> At arena \'Road\' Craig Adams scored 4 points.\n>>> At arena \'Home\' Maxim Afinogenov scored 12 points.\n>>> At arena \'Road\' Maxim Afinogenov scored 8 points.\n```\n',
    'author': 'Nathan',
    'author_email': 'nathansaccon10@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nsaccon/hockey_ref_scraper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
