# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['version_helper']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'version-helper',
    'version': '0.2.2a0',
    'description': 'Package for a better version management in python projects',
    'long_description': "# Version helper\n\n`version-helper` is a package for a better version management in python projects.\n\n_This package is still under development. Code may change frequently._\n\n[![PyPI](https://img.shields.io/pypi/v/version-helper)][version-helper-pypi]\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/version-helper)][version-helper-pypi]\n[![codecov](https://codecov.io/gh/dl6nm/version-helper/branch/main/graph/badge.svg?token=WNOMQ28E5J)](https://codecov.io/gh/dl6nm/version-helper)\n[![main](https://github.com/dl6nm/version-helper/actions/workflows/workflow.yml/badge.svg)](https://github.com/dl6nm/version-helper/actions/workflows/workflow.yml)\n[![Lines of code](https://img.shields.io/tokei/lines/github/dl6nm/version-helper)][version-helper-github]\n[![GitHub](https://img.shields.io/github/license/dl6nm/version-helper)](https://github.com/dl6nm/version-helper/blob/main/LICENSE.md)\n\n    from version_helper import Version\n    v = Version.get_from_git_describe()\n    print(v.core)  # major.minor.patch\n    print(v.full)  # major.minor.patch[-prerelease][+build]\n\n## Table of contents\n\n- [Version helper](#version-helper)\n  - [Table of contents](#table-of-contents)\n  - [Requirements](#requirements)\n  - [Installing `version-helper`](#installing-version-helper)\n  - [Usage](#usage)\n    - [Reading version from a file](#reading-version-from-a-file)\n    - [Writing version to a file](#writing-version-to-a-file)\n  - [Changelog](#changelog)\n  - [References](#references)\n\n## Requirements\n\n- [Python][python] 3.8+\n- [Git][git], if you'd need to receive a version string from `git describe`\n\n## Installing `version-helper`\n\n    pip install version-helper\n\n## Usage\n\n### Reading version from a file\n\n    import pathlib\n    from version_helper import Version\n    \n    version = Version.read_from_file(\n        file=pathlib.Path('/path/to/my/version_file.txt'),\n        variable_name='APP_VERSION',\n        separator='=',\n    )\n    print(version)\n\n### Writing version to a file\n\n    import pathlib\n    from version_helper import Version\n    \n    version = Version(1, 2, 3)\n    version.write_to_file(\n        file=pathlib.Path('/path/to/my/version_file.txt'),\n        variable_name='APP_VERSION',\n        separator='=',\n    )\n\n## Changelog\n\nAll notable changes to this project will be documented in the [CHANGELOG.md](CHANGELOG.md).\n\n## References\n\n- [git-describe](https://git-scm.com/docs/git-describe)\n- [Poetry](https://python-poetry.org/)\n- [Semantic Versioning](https://semver.org/)\n\n\n\n[git]: https://git-scm.com/\n[python]: https://www.python.org/\n\n[version-helper-github]: https://github.com/dl6nm/version-helper/\n[version-helper-pypi]: https://pypi.org/project/version-helper/\n",
    'author': 'DL6NM',
    'author_email': 'mail@dl6nm.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dl6nm/version-helper',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
