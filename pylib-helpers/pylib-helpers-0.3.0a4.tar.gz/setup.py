# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['helpers']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0']

setup_kwargs = {
    'name': 'pylib-helpers',
    'version': '0.3.0a4',
    'description': 'Helpers for common functional work done across several projects',
    'long_description': '# pylib-helpers\n\nHelpers for logging, sleeping, and other common functional work done across projects\n\n[![Release](https://github.com/samarthj/pylib-helpers/actions/workflows/release.yml/badge.svg)](https://github.com/samarthj/pylib-helpers/actions/workflows/release.yml)\n[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/samarthj/pylib-helpers?sort=semver)](https://github.com/samarthj/pylib-helpers/releases)\n[![PyPI](https://img.shields.io/pypi/v/pylib-helpers)](https://pypi.org/project/pylib-helpers/)\n\n[![Build](https://github.com/samarthj/pylib-helpers/actions/workflows/build_matrix.yml/badge.svg)](https://github.com/samarthj/pylib-helpers/actions/workflows/build_matrix.yml)\n\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)\n\n## RetryHandler\n\nSamples can be found here in the [tests](https://github.com/samarthj/pylib-helpers/blob/main/tests/test_retry_handler.py)\n',
    'author': 'Sam',
    'author_email': 'dev@samarthj.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/samarthj/pylib-helpers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
