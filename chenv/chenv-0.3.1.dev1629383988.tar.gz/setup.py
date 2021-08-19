# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['chenv',
 'chenv.models',
 'chenv.subcommands',
 'chenv.subcommands.blank',
 'chenv.subcommands.heroku',
 'chenv.subcommands.local',
 'chenv.subcommands.which']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'desert>=2020.11.18,<2021.0.0',
 'httpx>=0.16.1,<0.17.0',
 'marshmallow>=3.10.0,<4.0.0',
 'python-dotenv>=0.15.0,<0.16.0',
 'questionary>=1.9.0,<2.0.0',
 'toolz>=0.11.1,<0.12.0']

entry_points = \
{'console_scripts': ['chenv = chenv.main:main']}

setup_kwargs = {
    'name': 'chenv',
    'version': '0.3.1.dev1629383988',
    'description': 'modern local environment management',
    'long_description': ".. code-block:: text\n\n          _\n      ___| |__   ___ _ ____   __\n     / __| '_ \\ / _ | '_ \\ \\ / /\n    | (__| | | |  __| | | \\ V /\n     \\___|_| |_|\\___|_| |_|\\_/ . modern local environment management\n\n|Status| |PyPI| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |Status| image:: https://badgen.net/badge/status/alpha/d8624d\n   :target: https://badgen.net/badge/status/alpha/d8624d\n   :alt: Project Status\n.. |PyPI| image:: https://img.shields.io/pypi/v/chenv.svg\n   :target: https://pypi.org/project/chenv/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/chenv\n   :target: https://pypi.org/project/chenv\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/chenv\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/chenv/latest.svg?label=Read%20the%20Docs\n   :target: https://chenv.readthedocs.io/\n   :alt: Read the documentation at https://chenv.readthedocs.io/\n.. |Tests| image:: https://github.com/jonathan-shemer/chenv/workflows/Tests/badge.svg\n   :target: https://github.com/jonathan-shemer/chenv/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/jonathan-shemer/chenv/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/jonathan-shemer/chenv\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nThis command-line interface creates and manages local `.env` files from various sources.\n\nCoupled with `python-dotenv <https://pypi.org/project/python-dotenv/>`_ for python,\nor `dotenv <https://www.npmjs.com/package/dotenv/>`_ for node.js development,\nit provides better, more consistent environment variable management and developement.\n\nInstallation\n------------\n\nTo install `chenv`,\nrun this command in your terminal:\n\n.. code-block:: shell\n\n   $ pip install --user chenv\n\nAlso make sure that your :code:`$PATH` includes :code:`$HOME/.local/bin`.\nIf not, add this line to your :code:`.bashrc` / :code:`.zshrc`:\n\n.. code-block:: shell\n\n   export PATH=$HOME/.local/bin:$PATH;\n\nUsage\n-----\n\n`chenv`'s usage looks like:\n\n.. code-block:: shell\n\n   $ chenv COMMAND [ARGS]\n\nCommands currently include:\n\n=====\nblank\n=====\n\n   Choose to set `.env` as a new, blank, `.env.blank` file.\n\n======\nheroku\n======\n\n   Choose to set `.env` from a remote heroku app config-vars, as `.env.[app-name]`.\n\n   - -t <team>, --team <team>\n       Pre-fill team name\n\n   - -a <app>, --app <app>\n      Pre-fill app name\n\n=====\nlocal\n=====\n\n   Choose to set `.env` from a local, pre-exsiting `.env.*` file.\n\n   - filename\n      Pre-fill file-suffix name\n\nProject Configurations\n----------------------\n\n`chenv` also provides two file types that manipulate the output of new `.env.*` files being set.\n\n==========\n.envignore\n==========\n\n   Specifies intentionally unwanted environment-variables.\n   Each line in a envignore file specifies a pattern.\n\n   When deciding whether to ignore an environment variable, `chenv` checks it's key against the list of patterns described in this file.\n\n   :Pattern:\n      `.envignore` uses the unix filename pattern matching, similar to `.gitignore`'s, and as specified at https://docs.python.org/3/library/fnmatch.html\n\n=========\n.envmerge\n=========\n\n   Sepecifies environment variables to merge / override after any input is chosen. This provides consistency to preffered settings such as the `logging-level`, or `NODE_ENV` for local development usage in node.js.\n",
    'author': 'Jonathan Shemer',
    'author_email': 'i@jonathanshemer.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jonathan-shemer/chenv',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
