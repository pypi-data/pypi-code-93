# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_chuy_plugin']

package_data = \
{'': ['*']}

install_requires = \
['chuy==1.2.0', 'poetry>=1.1.7,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['chuy = poetry_chuy_plugin.plugin:ChuyPlugin']}

setup_kwargs = {
    'name': 'poetry-chuy-plugin',
    'version': '0.2.1',
    'description': 'Plugin to integrate Chuy with Poetry',
    'long_description': '# Poetry Chuy Plugin\n\n![CodeQL](https://github.com/UltiRequiem/poetry-chuy-plugin/workflows/CodeQL/badge.svg)\n![PyTest](https://github.com/UltiRequiem/poetry-chuy-plugin/workflows/PyTest/badge.svg)\n![Pylint](https://github.com/UltiRequiem/poetry-chuy-plugin/workflows/Pylint/badge.svg)\n[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)\n[![PyPi Version](https://img.shields.io/pypi/v/poetry-chuy-plugin)](https://pypi.org/project/poetry-chuy-plugin)\n![Repo Size](https://img.shields.io/github/repo-size/ultirequiem/poetry-chuy-plugin?style=flat-square&label=Repo)\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n![Lines of Code](https://img.shields.io/tokei/lines/github.com/UltiRequiem/poetry-chuy-plugin?color=blue&label=Total%20Lines)\n\nThis plugin integrates [Chuy](https://github.com/UltiRequiem/chuy) with\n[Poetry](https://github.com/python-poetry/poetry).\n\n_Note_: This only works in Poetry 1.2.0 or superior.\n\n## Installation\n\nFrom your terminal:\n\n```bash\npoetry plugin add poetry-chuy-plugin\n```\n\n## Configuration\n\nIn your `pyproject.toml`:\n\n```toml\n[tool.chuy]\nformat = "poetry run black ."\nlint = "poetry run pylint chuy tests"\ntests = "poetry run pytest"\npackage = "poetry build && poetry publish"\n```\n\n## Usage\n\n```bash\npoetry chuy tests\n```\n\nOr pass multiple arguments:\n\n```bash\npoetry chuy tests lint\n```\n\nSee [Chuy](https://github.com/UltiRequiem/chuy) for all the options.\n\n### License\n\nThis project is licensed under the [MIT License](https://github.com/UltiRequiem/poetry-chuy-plugin/blob/main/LICENSE).\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/poetry-chuy-plugin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
