# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grepy']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['grepy = grepy:main']}

setup_kwargs = {
    'name': 'grepy',
    'version': '0.1.2',
    'description': 'A Grep clone',
    'long_description': '# Grepy\n![CodeQL](https://github.com/UltiRequiem/grepy/workflows/CodeQL/badge.svg)\n![PyTest](https://github.com/UltiRequiem/grepy/workflows/PyTest/badge.svg)\n![Pylint](https://github.com/UltiRequiem/grepy/workflows/Pylint/badge.svg)\n[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)\n[![PyPi Version](https://img.shields.io/pypi/v/grepy)](https://pypi.org/project/grepy)\n![Repo Size](https://img.shields.io/github/repo-size/ultirequiem/grepy?style=flat-square&label=Repo)\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n![Lines of Code](https://img.shields.io/tokei/lines/github.com/UltiRequiem/grepy?color=blue&label=Total%20Lines)\n\nA Python clone of [Grep](https://en.wikipedia.org/wiki/Grep).\n\n## Install\n\nYou can install [grepy](https://pypi.org/project/grepy) from PyPI like any other package:\n\n```bash\npip install grepy\n```\n\nTo get the last version:\n\n```bash\npip install git+https:/github.com/UltiRequiem/grepy\n```\n\nIf you use Linux, you may need to install this with sudo to\nbe able to access the command throughout your system.\n\n## Usage\n\nSame as Grep:\n\n```bash\ngrepy "String to grep" file_to_grep.py\n```\n\n### License\n\nGrepy is licensed under the [MIT License](./LICENSE).\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/grep',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
