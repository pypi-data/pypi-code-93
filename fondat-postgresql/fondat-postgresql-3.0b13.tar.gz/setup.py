# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fondat']

package_data = \
{'': ['*']}

install_requires = \
['asyncpg>=0.21,<0.22', 'fondat-core>=3.0b87,<4.0']

setup_kwargs = {
    'name': 'fondat-postgresql',
    'version': '3.0b13',
    'description': 'PostgreSQL module for Fondat.',
    'long_description': '# fondat-postgresql\n\n[![PyPI](https://badge.fury.io/py/fondat-postgresql.svg)](https://badge.fury.io/py/fondat-postgresql)\n[![License](https://img.shields.io/github/license/fondat/fondat-postgresql.svg)](https://github.com/fondat/fondat-postgresql/blob/main/LICENSE)\n[![GitHub](https://img.shields.io/badge/github-main-blue.svg)](https://github.com/fondat/fondat-postgresql/)\n[![Test](https://github.com/fondat/fondat-postgresql/workflows/test/badge.svg)](https://github.com/fondat/fondat-postgresql/actions?query=workflow/test)\n[![Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n\nFondat module for PostgreSQL.\n\n## Develop\n\n```\npoetry install\npoetry run pre-commit install\n```\n\n## Test\n\n```\npoetry run pytest\n```\n',
    'author': 'fondat-postgresql authors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fondat/fondat-postgresql/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
