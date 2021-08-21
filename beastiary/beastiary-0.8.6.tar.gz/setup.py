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
    'version': '0.8.6',
    'description': '',
    'long_description': '![beastiary logo](https://beastiary.wytamma.com/images/logo.png)\n\n\n[![PyPi](https://img.shields.io/pypi/v/beastiary.svg)](https://pypi.org/project/beastiary/)\n[![tests](https://github.com/Wytamma/beastiary/actions/workflows/test.yml/badge.svg)](https://github.com/Wytamma/beastiary/actions/workflows/test.yml)\n[![cov](https://codecov.io/gh/Wytamma/beastiary/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/beastiary)\n[![docs](https://github.com/Wytamma/beastiary/actions/workflows/docs.yml/badge.svg)](https://beastiary.wytamma.com/)\n\nThis is a real time version of tracer that can be run on remote servers (e.g. a HPC). Its goal is to be a beautiful and simple, yet power tool for Bayesian phylogenetic inference.\n\n## Installation\n```bash\npip install beastiary\n```\n\n## Use\nTo start beastiary use the `beastiary` command. This will start the beastiary server. \n\n```bash\nbeastiary\n```\n\nThe server will start on [http://127.0.0.1:5000/](http://127.0.0.1:5000/) by default. Every time the server starts it will generate a unique id that can be used to log into the webapp. \n\nGo to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) and log in with the ID. \n\n![](docs/images/screen_shot.png)',
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
