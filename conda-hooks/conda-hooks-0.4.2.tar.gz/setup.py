# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['conda_hooks']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0']

entry_points = \
{'console_scripts': ['conda_env_store = conda_hooks.env_store:main']}

setup_kwargs = {
    'name': 'conda-hooks',
    'version': '0.4.2',
    'description': 'Keep anaconda environment files up to date',
    'long_description': '# conda-hooks\n\nKeep anaconda environment files up to date with installed packages.\nIn contrast to `conda export` it keeps the channel list intact, sorts packages alphabetically and does not purge `pip` dependencies.\nThis can easily be automated using [pre-commit](https://pre-commit.com/) hooks to automatically check for any missing packages before committing.\n\n[![Build Status](https://img.shields.io/github/workflow/status/f-koehler/conda-hooks/build)](https://github.com/f-koehler/conda-hooks/actions)\n[![codecov](https://codecov.io/gh/f-koehler/conda-hooks/branch/main/graph/badge.svg?token=4XHPAHUDOL)](https://codecov.io/gh/f-koehler/conda-hooks)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/f-koehler/conda-hooks/main.svg)](https://results.pre-commit.ci/latest/github/f-koehler/conda-hooks/main)\n[![PyPI Version](https://img.shields.io/pypi/v/conda-hooks)](https://pypi.org/project/conda-hooks/)\n![License](https://img.shields.io/pypi/l/conda-hooks?color=blue)\n\n## Installation\n\n### As a Python package\n\nThe `conda_hooks` package is installable as a normal python package, for example via pip:\n\n```bash\npip install conda_hooks\n```\n\n### As a `pre-commit` hook\n\nIn your `.pre-commit-config.yaml` file add\n\n```yaml\nrepos:\n  - repo: https://github.com/f-koehler/conda-hooks\n    rev: "0.4.1"\n    hooks:\n      - id: prettier\n```\n\n## Usage\n\n### Command line\n\nRunning `env_store --help` will print information about the available command line options.\nWe can either specify paths to environment file explicitly\n\n```bash\nconda_env_store environment1.yml env2.yaml src/env3.yml\n```\n\nor use globbing patterns like this:\n\n```bash\nconda_env_store -g **/environment.yml -g **/env.yml\n```\n\nOf course we can combine both methods:\n\n```bash\nconda_env_store -g src/env*.yml environment.yml\n```\n\n### As a `pre-commit` hook\n\nWhen using the `pre-commit` hook we can use the same command line arguments, so please refer to the section above.\nAn example using globbing patterns would be:\n\n```yaml\nrepos:\n  - repo: https://github.com/f-koehler/conda-hooks\n    rev: "0.4.1"\n    hooks:\n      - id: prettier\n        args: ["-g", "**/environment.yml"]\n```\n\n## Roadmap\n\nCurrently missing features that should be implemented in the near future:\n\n- handle pinned versions\n',
    'author': 'Fabian Köhler',
    'author_email': 'fabian.koehler@protonmail.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/f-koehler/conda-hooks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
