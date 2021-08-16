# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beastiary',
 'beastiary.api',
 'beastiary.api.endpoints',
 'beastiary.crud',
 'beastiary.db',
 'beastiary.models',
 'beastiary.schemas']

package_data = \
{'': ['*'],
 'beastiary': ['webapp-dist/*',
               'webapp-dist/css/*',
               'webapp-dist/img/icons/*',
               'webapp-dist/js/*']}

install_requires = \
['SQLAlchemy>=1.4.22,<2.0.0',
 'aiofiles<0.6.0',
 'fastapi[all]>=0.67.0,<0.68.0',
 'typer[all]>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['beastiary = beastiary.cli:app']}

setup_kwargs = {
    'name': 'beastiary',
    'version': '0.8.2',
    'description': '',
    'long_description': "![beastiary logo](docs/images/logo.png)\n\n\n[![PyPi](https://img.shields.io/pypi/v/beastiary.svg)](https://pypi.org/project/beastiary/)\n[![tests](https://github.com/Wytamma/beastiary/actions/workflows/test.yml/badge.svg)](https://github.com/Wytamma/beastiary/actions/workflows/test.yml)\n[![cov](https://codecov.io/gh/Wytamma/beastiary/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/beastiary)\n[![docs](https://github.com/Wytamma/beastiary/actions/workflows/docs.yml/badge.svg)](https://beastiary.wytamma.com/)\n\nThis is a replacement for tracer. It's feature feature is the real time aspect. Secondly it's modern looking. 3rd it has improved features. \n\n\n## CLI\nLaunch the app\nCan point to log file to autostart watcher\n\n## Webapp \nVue\nPlotly\n\n## Web API\nFastAPI that sends data to and from DB and servers the webapp\nCan start file watchers\n\n## Watcher \nPython class that watches files and updates DB with changes.\n\n\n## BD (MEMORY)\nProtected by the CRUD\n\n\n## distribution \nCLI vs app (just launches web browser)\nhttps://docs.python-guide.org/shipping/freezing/\n",
    'author': 'Wytamma Wirth',
    'author_email': 'wytamma.wirth@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
