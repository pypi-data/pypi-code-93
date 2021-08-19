# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pfzy']

package_data = \
{'': ['*']}

extras_require = \
{'docs': ['Sphinx>=4.1.2,<5.0.0',
          'furo>=2021.8.17-beta.43,<2022.0.0',
          'myst-parser>=0.15.1,<0.16.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0']}

setup_kwargs = {
    'name': 'pfzy',
    'version': '0.2.0',
    'description': 'Python port of the fzy fuzzy string matching algorithm',
    'long_description': "# pfzy\n\n<!-- start elevator-pitch -->\n\n[![CI](https://github.com/kazhala/pfzy/workflows/CI/badge.svg)](https://github.com/kazhala/pfzy/actions?query=workflow%3ACI)\n[![Build](https://codebuild.ap-southeast-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiT2pwUFo2MVBzV1ptL0d4VDhmSHo4bSswVHFuaEh6bEU1d2g3bmpsdnZjSzcwWkxac3NHcjBKZDkyT2t1R0VveHJ0WlNFWmZmUjNQUGFpemxwV2loRm9rPSIsIml2UGFyYW1ldGVyU3BlYyI6Imw4dlcwYjlxaU9kYVd0UkoiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)](https://ap-southeast-2.console.aws.amazon.com/codesuite/codebuild/378756445655/projects/pfzy/history?region=ap-southeast-2&builds-meta=eyJmIjp7InRleHQiOiIifSwicyI6e30sIm4iOjIwLCJpIjowfQ)\n[![Coverage](https://img.shields.io/coveralls/github/kazhala/pfzy?logo=coveralls)](https://coveralls.io/github/kazhala/pfzy?branch=master)\n[![Version](https://img.shields.io/pypi/pyversions/pfzy)](https://pypi.org/project/pfzy/)\n[![PyPi](https://img.shields.io/pypi/v/pfzy)](https://pypi.org/project/pfzy/)\n[![License](https://img.shields.io/pypi/l/pfzy)](https://github.com/kazhala/pfzy/blob/master/LICENSE)\n\nPython port of the [fzy](https://github.com/jhawthorn/fzy) fuzzy string matching algorithm.\n\n## Requirements\n\n```\npython >= 3.7\n```\n\n## Background\n\n[fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) is a famous python package for performing fuzzy matching\nbetween strings powered by [python-Levenshtein](https://github.com/miohtama/python-Levenshtein). While it does its\njob well it doesn't calculate/provide the matching indices which is essential in a fuzzy finder applications.\n\nThe [fzy](https://github.com/jhawthorn/fzy) fuzzy matching algorithm can calculate the matching score while also\nproviding the matching indices which fuzzy finder applications can use to provide extra highlights.\n\nThe initial implementation of this algorithm can be found at [sweep.py](https://github.com/aslpavel/sweep.py) which\nis a python implementation of the terminal fuzzy finder. The code snippet is later used by the project [vim-clap](https://github.com/liuchengxu/vim-clap).\n\n**I found myself needing this logic across multiple projects hence decided to strip out the logic and publish a dedicated\npackage with detailed documentation and unittest.**\n\n## Credit\n\n- [fzy](https://github.com/jhawthorn/fzy)\n- [sweep.py](https://github.com/aslpavel/sweep.py)\n- [vim-clap](https://github.com/liuchengxu/vim-clap)\n\n## LICENSE\n\n> All 3 projects mentioned in [Credit](#credit) are all licensed under [MIT](https://opensource.org/licenses/MIT).\n\nThis project is licensed under [MIT](https://github.com/kazhala/pfzy). Copyright (c) 2021 Kevin Zhuang\n\n<!-- end elevator-pitch -->\n",
    'author': 'Kevin Zhuang',
    'author_email': 'kevin7441@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kazhala/pfzy',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
