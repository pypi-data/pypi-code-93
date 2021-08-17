# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['boxie']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['boxie = boxie:main']}

setup_kwargs = {
    'name': 'boxie',
    'version': '1.2.0',
    'description': 'Like Figlet but puts the text in a box',
    'long_description': '# boxie\n\n[![Mit License Icon](https://black.readthedocs.io/en/stable/_static/license.svg)](https://github.com/UltiRequiem/boxie/blob/main/LICENSE)\n[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Total Lines](https://img.shields.io/tokei/lines/github.com/UltiRequiem/boxie?color=blue&label=Total%20Lines)](https://github.com/UltiRequiem/boxie)\n![CodeQL](https://github.com/UltiRequiem/boxie/workflows/CodeQL/badge.svg)\n![Pylint](https://github.com/UltiRequiem/boxie/workflows/Pylint/badge.svg)\n![Repo Size](https://img.shields.io/github/repo-size/ultirequiem/boxie?style=flat-square&label=Repo)\n[![PyPi Version](https://img.shields.io/pypi/v/boxie)](https://pypi.org/project/boxie)\n[![Total Downloads](https://pepy.tech/badge/boxie)](https://pepy.tech/project/boxie)\n\nA command line utility to put text in a box.\n\n## Installation\n\n```bash\npip install boxie\n```\n\nTo get the last version:\n\n```bash\npip install git+https:/github.com/UltiRequiem/boxie\n```\n\nIf you are on Linux you may need to use sudo to access this globally.\n\n## Usage\n\n```bash\nboxie "Hello World"\n```\n\nOr...\n\n```bash\npython -m boxie "Hello World"\n```\n\nOr in your code:\n\n```python\nfrom boxie import boxier\n\nboxier("Hello World")\n```\n\n### Screenshot\n\n![Screenshot](./assets/screenshot.png)\n\n### LICENSE\n\nThis project is licensed under the [MIT](./LICENSE) License.\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/boxie',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
