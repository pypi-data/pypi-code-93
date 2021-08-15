# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notion_backup']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.10.0',
 'click>=7.1.2',
 'prompt_toolkit>=3.0.5',
 'requests>=2.23.0',
 'tqdm>=4.46.0']

entry_points = \
{'console_scripts': ['backup_notion = notion_backup.backup_service:main']}

setup_kwargs = {
    'name': 'notion-backup',
    'version': '0.3.0',
    'description': 'Notion workspace export automation tool',
    'long_description': "# notion-backup\nAutomate export of Notion workspace\n\n\n## Installation\n\n```\npip install --upgrade notion-backup\n```\n\n\n## Usage\n\n```\nbackup_notion --output-dir='.'\n```\n\n## How it works\n\nThe script obtains an API token by requesting a temporary password to be sent to your email address.\n\nLogin information are stored in `~/.notion_backup.conf`\n\nThe export zip is generated and downloaded to the specified directory.\n",
    'author': 'Ligohu',
    'author_email': 'ligohu@outlook.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/HugoLime/notion-backup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.5',
}


setup(**setup_kwargs)
