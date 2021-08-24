# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['canopy', 'canopy.templates']

package_data = \
{'': ['*'], 'canopy': ['static/*'], 'canopy.templates': ['archive/*']}

install_requires = \
['understory>=0.0.60,<0.0.61']

entry_points = \
{'web.apps': ['canopy = canopy:app']}

setup_kwargs = {
    'name': 'canopy-network',
    'version': '0.0.49',
    'description': 'A decentralized social network of personal websites',
    'long_description': '# canopy\nA decentralized social network of personal websites\n\nStore and display content on your own personal website. Interact richly\nwith other sites.\n\n## Install\n\nDebian/Ubuntu: `wget understory.cloud/gaea.py -q && python3 gaea.py --deploy canopy/canopy`\n\n### Manually\n\n    $ pip install canopy-network\n    $ web serve canopy\n\n## Features\n\n* render profile, pages, media, posts and feeds with semantic markup a la [microformats](https://indieweb.org/microformats)\n  * archive source material for [reply contexts](https://indieweb.org/reply-context)\n  * moderated threaded discussion using Webmentions with Salmention & Vouch\n  * syndicate to third-party aggregators\n* store posts:\n  * as [queryable JSON](https://www.sqlite.org/json1.html) in SQLite database\n    * [full-text search](https://www.sqlite.org/fts5.html)\n  * as JSON flat files inside Git repository for change history\n* follow by subscribing and publish to subscribers using WebSub\n* sign in to third-party applications using IndieAuth\n  * leverage third-party Micropub editors\n  * leverage third-party Microsub readers\n* import/export tools\n  * syndicate/backfeed to/from Twitter/Github/Facebook\n  * backup/restore to/from local/remote storage\n',
    'author': 'Angelo Gladding',
    'author_email': 'angelo@lahacker.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://understory.cloud/canopy.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
