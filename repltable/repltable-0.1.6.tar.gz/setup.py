# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repltable']

package_data = \
{'': ['*']}

install_requires = \
['replit>=3.2.1,<4.0.0']

setup_kwargs = {
    'name': 'repltable',
    'version': '0.1.6',
    'description': 'Table support for the replit database',
    'long_description': "# repltable\n\n![PyPI - Downloads](https://img.shields.io/pypi/dm/repltable?style=for-the-badge)\n![code style](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge&logo=python)\n\nthis is a project is to make it so that you can have tables in the replit db.\n\nthe main annoyance (for me) with replit is that it reverts a lot of database file changes, which forces you to use the repl.it database.\n\n## installation \n```bash\npip install repltable\n```\n\n## usage\n```python\nimport repltable\nfrom replit import db\n\ndatabase = repltable.Database(db)\n\n# repltable databases work like a dictionary\ndatabase['table'].get(foo='bar')\n>>> [{'foo': 'bar'}]\n\n# repltable auto-creates tables if they don't exist\ntable = database['nonexistenttable']\ntable.insert(dict(foo='bar'))\n\n# you can get one, or get all matching documents\ntable.get_one(foo='bar')\n>>> {'foo': 'bar'}\n```\n\n## contributing\nto contribute, fork the repo, make a branch, and send a pull request.\n\nfor local development, you can install the dependencies with poetry:\n```bash\npoetry install\n```\n\n## license\n[MIT](https://choosealicense.com/licenses/mit/)\n",
    'author': 'terabyte.',
    'author_email': 'mikey@mikeyo.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/terabyte3/repltable',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
