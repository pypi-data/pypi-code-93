# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lihim']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.4.0,<2.0.0', 'peewee>=3.14.4,<4.0.0', 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['lihim = lihim.main:app']}

setup_kwargs = {
    'name': 'lihim',
    'version': '1.0.2',
    'description': 'CLI for managing secret keys, tokens, sensitive and/or public key-value pairs.',
    'long_description': '# lihim\nCLI tool for managing secret keys, tokens, sensitive and/or public key-value pairs. AKA *"A note-taking CLI tool glorified by added security and complexity for listing key-value pairs."*\n\n\n## Overview\n**Lihim** (Filipino word for *secret*) uses PyNaCl\'s `SecretBox` for secret key encryption, and stores the key-value pairs in an SQLite (PostgreSQL coming soon) database. Secret keys are managed according to users and groups. That is, each user has groups and these groups can contain several key-value pairs.\n\n![lihim-chart](https://res.cloudinary.com/nvqacloud/image/upload/v1628687874/lihim_chart_nwir6s.png)\n\n\n## Installation\n```cli\npip install lihim\n```\n\n\n## Get Started\n1. Run `lihim initdb` to create the database and tables,\n2. Next, `lihim useradd [username]` to add your first user. You may read [Notes](#notes) section > Re: Users\' key for prompts to expect.\n3. Then, `lihim login [username]` to login.\n4. Before you can add key-value pairs, you need a group. Run `lihim groupadd [group name]` to create a group.\n5. Now you can add a pair. `lihim pairadd` command will prompt interactively for key, value, and group.\n6. You just added your first key-val pair! Refer to [Commands](#commands) section below for more commands.\n\n\n## Commands\n| Command  | Description |\n| ------------- | ------------- |\n| `initdb` | One-off command to create the database and tables. |\n| `users` | Check registered users. |\n| `useradd [username]` | Create a new user with username of ____. |\n| `login [username]` | Login as user with username of ____. |\n| `logout` | Logout current user. |\n| `check` | Check who is currently logged in. |\n| `groups` | Display all the groups of current user. |\n| `group [group name]` | Display all the keys of key-value pairs in the group with name of ____. |\n| `groupadd [group name]` | Add new group with name of ____. |\n| `groupdel [group name]` | Delete group with name of ____ |\n| `pairs` | Display all the keys of available pairs of the current user. |\n| `pair [key]` | Display the key-value pair with key of ____. |\n| `pairadd` | Add a new key-value pair. Will prompt interactively for key, value, and group. |\n| `pairdel [key] [group name]` | Delete pair with key ____ and within group ____. |\n\n\n## Notes\n### Re: User\'s "key"\nAs per [PyNaCl\'s documentation](https://pynacl.readthedocs.io/en/latest/secret/#requirements):\n\n> The 32 bytes key given to `SecretBox` must be kept secret. It is the combination to your “safe” and anyone with this key will be able to decrypt the data, or encrypt new data.\n\nIn lihim, this "key" is generated when *creating* a new user. The key\'s path (where to put it) and name (unique, only you knows) are all up to the user. When creating a user by `useradd [username]`, there will be prompts asking where and what to name the key. This is only for generating the key and the user **can (absolutely) rename and/or move** the key elsewhere anytime. The key\'s path and name are not stored in the database.\n\nWhen logging in, there will be prompts asking where your key is and what is its name. This happens every `login [username]`. You must give the current key path and key name if you ever moved and/or renamed the key.\n\n### Re: SQLite3\nThe project currently uses sqlite. Postgresql option is on the roadmap. All values of key-value pairs are encrypted using PyNaCl\'s `SecretBox`.\n\n\n## Development\nThe project uses poetry to package and manage dependencies:\n```cli\npoetry install\n```\n\nRun tests:\n```cli\npoetry pytest\n```\n\n\n## License\nMIT License\n\nCopyright (c) 2021 Neil Van\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.',
    'author': 'Neil Van',
    'author_email': 'nvq.alino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
