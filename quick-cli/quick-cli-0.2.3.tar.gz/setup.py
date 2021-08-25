# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quick',
 'quick.commands',
 'quick_client',
 'quick_client.api',
 'quick_client.models']

package_data = \
{'': ['*'], 'quick_client': ['docs/*']}

install_requires = \
['PyYAML>=5.3,<6.0',
 'isodate>=0.6.0,<0.7.0',
 'python-dateutil>=2.5.0,<3.0.0',
 'requests>=2.0.0,<3.0.0',
 'six>=1.12.0,<2.0.0',
 'urllib3>=1.0,<2.0']

entry_points = \
{'console_scripts': ['quick = quick.__main__:main']}

setup_kwargs = {
    'name': 'quick-cli',
    'version': '0.2.3',
    'description': 'The CLI to control your quick cluster.',
    'long_description': '# quick CLI\n\n![Tests](https://github.com/bakdata/quick-cli/workflows/Test%20quick-cli/badge.svg)\n![Code Quality](https://github.com/bakdata/quick-cli/workflows/Code%20Quality/badge.svg)\n\n```\n> quick -h\n\nusage: quick [-h] command [options ...] ...\n\nControl your quick deployment.\n\nAvailable commands:\n  command [options ...]\n    context              Manage quick configuration\n    topic                Manage topics\n    gateway              Manage gateways\n    mirror               Manage mirrors\n    app                  Manage streams applications\n```\n\n### Commands\n\nSee [commands.md](commands.md) for more information about available commands in the CLI.\n',
    'author': 'd9p',
    'author_email': 'contact@d9p.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://d9p.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
