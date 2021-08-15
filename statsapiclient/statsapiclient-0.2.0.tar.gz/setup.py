# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['statsapiclient', 'statsapiclient.shifts']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.8.2,<5.0.0', 'requests>=2.22,<3.0']

setup_kwargs = {
    'name': 'statsapiclient',
    'version': '0.2.0',
    'description': 'A wrapper around the NHL’s JSON API.',
    'long_description': "# statsapiclient: A client for the NHL stats API\n\n[![PyPI version](https://badge.fury.io/py/statsapiclient.svg)](https://pypi.org/project/statsapiclient)\n\n[![CircleCI](https://circleci.com/gh/bplabombarda/statsapiclient.svg?style=svg)](https://circleci.com/gh/bplabombarda/statsapiclient)\n\n## Purpose\n\nTo provide a Python client to access the NHL's JSON API including game, play, and player data.\n\n\n## Installation\n\n    pip install statsapiclient\n\n\n## Modules\n\n### Schedule\n\n`games`\n\nA list of games contained within the instantiated date or date range.\n\n\n### Games\n\n#### game\n\n`json`\n\nRaw JSON response data.\n\n`box_score`\n\nBox score object.\n\n`line_score`\n\nLine score object.\n\n`plays`\n\nPlay object.\n\n\n### Team\n\n`get_active`\n\nReturns a list of all active teams.\n\n`get_active_by_conference`\n\nReturns a list of all active teams in a given conference.\n\n`get_active_by_division`\n\nReturns a list of all active teams in a given division.\n\n\n### Examples\n\nGames from date:\n      \n    from statsapiclient.schedule import Schedule\n\n\n    s = Schedule('2019-01-01')\n    print(s.games[0]['gamePk'])    # 2018020612\n\nGame data:\n\n    from statsapiclient.games import Game\n\n    g = Game('2018020612')\n\n    box_score = g.box_score\n    line_score = g.line_score\n    play_by_play = g.plays\n\nPlay data:\n\n    g.plays.all_plays                   # All plays\n    g.plays.get_plays_by_period(1)      # All plays in the first period\n    g.plays.get_penalty_plays()         # All penalty plays\n    g.plays.get_scoring_plays()         # All scoring plays\n",
    'author': 'Brett LaBombarda',
    'author_email': 'bplabombarda@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bplabombarda/statsapiclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
