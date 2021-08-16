# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['just_a_test_project', 'just_a_test_project.package1']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'just-a-test-project',
    'version': '0.0.7',
    'description': 'A project for testing https://github.com/creditornot/wolt-python-package-cookiecutter',
    'long_description': '# Just a test project\n![PyPI](https://img.shields.io/pypi/v/just-a-test-project?style=flat-square)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/just-a-test-project?style=flat-square)\n![PyPI - License](https://img.shields.io/pypi/l/just-a-test-project?style=flat-square)\n\nA project for testing https://github.com/creditornot/wolt-python-package-cookiecutter\n\n## Installation\n\n```sh\npip install just-a-test-project\n```\n\n## Development\n1. Clone this repository\n2. Create a virtual environment and install the dependencies\n\n   ```sh\n   poetry install\n   ```\n\n3. Activate the virtual environment\n\n   ```sh\n   poetry shell\n   ```\n\n### Testing\n\n```sh\npytest\n```\n\n### Pre-commit\n\nPre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality\n checks to make sure the changeset is in good shape before the commit/push happens.\n\nYou can install the hooks with (runs for each commit):\n\n```sh\npre-commit install\n```\n\nOr if you want them to run only for each push:\n\n```sh\npre-commit install -t pre-push\n```\n',
    'author': 'Jerry Pussinen',
    'author_email': 'jerry.pussinen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/creditornot/just-a-test-project',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
