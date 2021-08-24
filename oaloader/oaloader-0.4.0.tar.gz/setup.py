# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oaloader']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'loguru>=0.5.3,<0.6.0',
 'pywin32>=300,<301',
 'tabulate>=0.8.9,<0.9.0',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['oaloader = oaloader.__main__:cli']}

setup_kwargs = {
    'name': 'oaloader',
    'version': '0.4.0',
    'description': 'A handy tool to manage your office addins locally, you can use it for addin development or deploy your addins for your clients out of AppSource.',
    'long_description': "# Office Addin Sideloader\n\n[![PyPI](https://img.shields.io/pypi/v/oaloader?style=flat-square)](https://pypi.org/project/oaloader/)\n![GitHub](https://img.shields.io/github/license/elonzh/office-addin-sideloader?style=flat-square)\n\nA handy tool to manage your office addins locally,\nyou can use it for addin development or deploy your addins for your clients out of AppSource.\n\n> NOTE: currently only support windows.\n\n## Features\n\n- Add or remove Office Add-in locally.\n- Support local or url manifest source.\n- Debug sideload status and list manifest info.\n- Single binary without any dependency.\n- Use it as a library.\n- Generate add-in installer/uninstaller with [sentry](https://sentry.io) support by single command.\n- Support fixing add-in [APP ERROR](https://docs.microsoft.com/en-us/office365/troubleshoot/installation/cannot-install-office-add-in) and [clearing cache](https://docs.microsoft.com/en-us/office/dev/add-ins/testing/clear-cache).\n\n## Installation\n\n### Pre-built releases\n\nIf you just use the command line and don't have a python environment,\ndownload pre-built binary from [GitHub Releases](https://github.com/elonzh/office-addin-sideloader/releases).\n\n### Pypi\n\n```shell\n> pip install oaloader\n```\n\n## Quick Start\n\n```text\n> ./oaloader.exe --help\nUsage:  [OPTIONS] COMMAND [ARGS]...\n\n  Manage your office addins locally.\n\nOptions:\n  --version         Show the version and exit.\n  -l, --level TEXT  The log level  [default: info]\n  --help            Show this message and exit.\n\nCommands:\n  add     Register catalog and add manifests, manifests can be file paths\n          or...\n\n  fix     Try fixing `APP ERROR` when starting up add-ins.\n  info    Debug sideload status.\n  remove  Remove manifest from catalog and manifest can be a file path or...\n```\n\n## Build an Addin installer\n\n1. Install [Poetry](https://python-poetry.org/docs/).\n2. Run `poetry install` to prepare environment.\n3. Run `poetry run invoke installer -m <YOUR-ADDIN-MANIFEST-URL>` to build your own installer.\n\nIf your want customize the installer, just edit `installer.jinja2` or write your own installer with `oaloader` module.\n\n## Build an Addin uninstaller\n\nJust using invoke `uninstaller` task like `installer` above.\n\n## How it works\n\nhttps://docs.microsoft.com/en-us/office/dev/add-ins/testing/create-a-network-shared-folder-catalog-for-task-pane-and-content-add-ins\n",
    'author': 'elonzh',
    'author_email': 'elonzh@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/elonzh/office-addin-sideloader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
