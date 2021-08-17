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
    'version': '0.0.19',
    'description': 'A project for testing https://github.com/creditornot/wolt-python-package-cookiecutter',
    'long_description': "# Just a test project\n![PyPI](https://img.shields.io/pypi/v/just-a-test-project?style=flat-square)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/just-a-test-project?style=flat-square)\n![PyPI - License](https://img.shields.io/pypi/l/just-a-test-project?style=flat-square)\n---\n\n**Documentation**: [https://creditornot.github.io/just-a-test-project](https://creditornot.github.io/just-a-test-project)\n\n\n**PyPI**: [https://pypi.org/project/just-a-test-project/](https://pypi.org/project/just-a-test-project/)\n\n---\n\nA project for testing wolt-python-package-cookiecutter\n\n## Installation\n\n```sh\npip install just-a-test-project\n```\n\n## Development\n* Clone this repository\n* Create a virtual environment and install the dependencies\n\n```sh\npoetry install\n```\n\n* Activate the virtual environment\n\n```sh\npoetry shell\n```\n\n### Testing\n\n```sh\npytest\n```\n\n### Documentation\nThe documentation is automatically generated from the content of the [docs directory](./docs) and from the docstrings\n of the public signatures of the source code. The documentation is updated and published as a [Github project page\n ](https://pages.github.com/) automatically as part each release.\n\n### Releasing\nThe project uses [semantic versioning](https://semver.org/). Use `v` in front of the major version number.\n\nWhen you want to make a release, create and push a tag:\n\n```sh\ngit tag v1.2.3\ngit push origin v1.2.3\n```\n\nThis triggers [draft_release](.github/workflows/draft_release.yml) workflow which updates the changelog\n and creates a draft release in GitHub. Find the draft release from the [GitHub releases](https://github.com\n /creditornot/just-a-test-project/releases) and publish it.\n\nWhen a release is published, it'll trigger [release](.github/workflows/release.yml) workflow which creates PyPI\n release and deploys updated documentation.\n\n\n### Pre-commit\n\nPre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality\n checks to make sure the changeset is in good shape before a commit/push happens.\n\nYou can install the hooks with (runs for each commit):\n\n```sh\npre-commit install\n```\n\nOr if you want them to run only for each push:\n\n```sh\npre-commit install -t pre-push\n```\n\nOr if you want e.g. want to run all checks manually for all files:\n```sh\npre-commit run --all-files\n```\n",
    'author': 'Jerry Pussinen',
    'author_email': 'jerry.pussinen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://creditornot.github.io/just-a-test-project',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
