# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chuy']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0']

entry_points = \
{'console_scripts': ['chuy = chuy:main']}

setup_kwargs = {
    'name': 'chuy',
    'version': '1.2.0',
    'description': 'Set alias to long commands and speed up your workflow.',
    'long_description': '# Chuy\n\n![CodeQL](https://github.com/UltiRequiem/chuy/workflows/CodeQL/badge.svg)\n![PyTest](https://github.com/UltiRequiem/chuy/workflows/PyTest/badge.svg)\n![Pylint](https://github.com/UltiRequiem/chuy/workflows/Pylint/badge.svg)\n[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)\n[![PyPi Version](https://img.shields.io/pypi/v/chuy)](https://pypi.org/project/chuy)\n![Repo Size](https://img.shields.io/github/repo-size/ultirequiem/chuy?style=flat-square&label=Repo)\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n![Lines of Code](https://img.shields.io/tokei/lines/github.com/UltiRequiem/chuy?color=blue&label=Total%20Lines)\n\nSet alias to long commands and speed up your workflow,\ninspired in tools like [yarn](https://yarnpkg.com) and [npm](https://github.com/npm/cli).\n\nAlthough Chuy is written in Python, it can be used for projects of any language,\nand even folders that are not projects!\n\n**Note:** this tool is actively used by its primary author.\nHe\'s happy to review pull requests / respond to issues you may discover.\n\n## Install\n\nYou can install [Chuy](https://pypi.org/project/chuy) from PyPI like any other package:\n\n```bash\npip install chuy\n```\n\nTo get the last version:\n\n```bash\npip install git+https:/github.com/UltiRequiem/chuy\n```\n\nIf you use Linux, you may need to install this with sudo to\nbe able to access the command throughout your system.\n\n## Example Configuration file\n\n```json\n{\n  "format": "poetry run black .",\n  "lint": "poetry run pylint chuy tests",\n  "tests": "poetry run pytest",\n  "package": "poetry build && poetry publish"\n}\n```\n\nThis configuration must be in a [`chuy.json`](./chuy.json) file.\nUsually this file goes in the root of your project but it can really go anywhere.\n\n## Usage\n\nAfter having defined the commands in the [chuy.json](./chuy.json) file,\nyou can now execute them as follows:\n\n```bash\nchuy format\n $ poetry run black .\n ....\n```\n\nThis varies depending on the commands you\nhave written in the [chuy file](#example-configuration-file).\n\n```bash\nchuy lint\n $ poetry run pylint chuy tests\n ....\n```\n\nYou can also pass multiple commands:\n\n```bash\nchuy lint format tests\n $ poetry run pylint chuy tests\n ....\n\n $ poetry run black .\n ....\n\n $ poetry run pytest\n ....\n```\n\n### Tricks\n\nIf you do not pass any command, you will get a menu with all the available commands,\nthen you will be asked which of them you want to execute,\nhere you can pass more than one command if you want.\n\n### Screenshots\n\nNormal usage:\n\n![Screenshot Normal Usage](https://i.imgur.com/sOu86gu.png)\n\nAnd if you don\'t pass any command:\n\n![Screenshot Menu](https://i.imgur.com/nFd4Bz9.png)\n\n### License\n\nChuy is licensed under the [MIT License](./LICENSE).\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/chuy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
