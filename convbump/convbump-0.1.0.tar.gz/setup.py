# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['convbump', 'convbump.versions']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.2.0,<22', 'click>=8.0.1,<9.0.0', 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['convbump-changelog = convbump.app:changelog',
                     'convbump-version = convbump.app:version']}

setup_kwargs = {
    'name': 'convbump',
    'version': '0.1.0',
    'description': 'Manage changelog and bump project version number using conventional commits from latest git tag.',
    'long_description': '# ConvBump\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Latest Version](https://img.shields.io/pypi/v/convbump.svg)](https://pypi.org/project/convbump/)\n[![BSD License](https://img.shields.io/pypi/l/convbump.svg)](https://github.com/playpauseandstop/convbump/blob/master/LICENSE)\n\nA simple tool that reads Git history and returns the next version and changelog\nbased on conventional commits.\n\n\n## Attribution\nThis project is forked from [Badabump created by Igor Davydenko](https://github.com/playpauseandstop/badabump).\n\n## Notice\nThis project is a heavily modified fork that solves our specific needs. We\ndiscourage anyone from using it and we will offer no support to anyone. Checkout\n[Badabump](https://github.com/playpauseandstop/badabump) for a more general\ntool.\n\n## Development\nThe application is written in Python and uses\n[Poetry](https://python-poetry.org/docs/) to configure the package and manage\nits dependencies.\n\nMake sure you have [Poetry CLI installed](https://python-poetry.org/docs/#installation).\nThen you can run\n\n    $ poetry install\n\nwhich will install the project dependencies (including `dev` dependencies) into a\nPython virtual environment managed by Poetry (alternatively, you can activate\nyour own virtual environment beforehand and Poetry will use that).\n\n### Run tests with pytest\n\n    $ poetry run pytest\n\nor\n\n\t$ poetry shell\n\t$ pytest\n\n`pytest` will take configuration from `pytest.ini` file first (if present), then\nfrom `pyproject.toml`. Add any local configuration to `pytest.ini`.\nConfiguration in `pyproject.toml` will be used in Teamcity. You can run your\ntests the same way as Teamcity to catch any errors\n\n\t$ pytest -c pyproject.toml\n\n### Code formatting\nThe application is formatted using [black](https://black.readthedocs.io/en/stable/) and [isort](https://pycqa.github.io/isort/).\nYou can either run black and isort manually or use prepared [Poe](https://github.com/nat-n/poethepoet) task to format the whole project.\n\n\t$ poetry run poe format_code\nor\n\n\t$ poetry shell\n\t$ poe format_code\n',
    'author': 'Max Kovykov',
    'author_email': 'kovykmax@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Luminaar/convbump',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
