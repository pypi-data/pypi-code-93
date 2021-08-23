# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ephemetoot']

package_data = \
{'': ['*']}

install_requires = \
['mastodon.py>=1.4.3,<2.0.0', 'pyyaml>=5.0,<6.0', 'requests>=2.22.0,<3.0.0']

entry_points = \
{'console_scripts': ['ephemetoot = ephemetoot.console:main']}

setup_kwargs = {
    'name': 'ephemetoot',
    'version': '3.1.2',
    'description': 'A command line tool to delete your old toots',
    'long_description': '# 🥳 ==> 🧼 ==> 😇\n\n## Prior work\nThe initial `ephemetoot` script was based on [this tweet-deleting script](https://gist.github.com/flesueur/bcb2d9185b64c5191915d860ad19f23f) by [@flesueur](https://github.com/flesueur)\n\n`ephemetoot` relies heavily on the [Mastodon.py](https://pypi.org/project/Mastodon.py/) package by [@halcy](https://github.com/halcy)\n\n## Usage\n\nYou can use `ephemetoot` to delete [Mastodon](https://github.com/tootsuite/mastodon) toots that are older than a certain number of days (default is 365). Toots can optionally be saved from deletion if:\n* they are pinned; or\n* they include certain hashtags; or\n* they have certain visibility; or\n* they are individually listed to be kept\n\nThere are various options controlling timing, scheduling, and output.\n\nRun from the command line with `ephemetoot`.\n\nRun `ephemetoot --help` or read the docs for all options.\n\n## Contributing\n\nephemetoot is packaged using `poetry` and tested using `pytest`.\n\nFor all bugs, suggestions, pull requests or other contributions, please check the [contributing guide](https://github.com/hughrun/ephemetoot/blob/master/docs/contributing.md).\n',
    'author': 'Hugh Rundle',
    'author_email': 'ephemetoot@hugh.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ephemetoot.hugh.run',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
