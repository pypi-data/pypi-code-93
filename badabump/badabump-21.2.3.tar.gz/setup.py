# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['badabump', 'badabump.ci', 'badabump.cli', 'badabump.versions']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.2.0,<22', 'tomli>=1.2.0,<2.0.0']

entry_points = \
{'console_scripts': ['badabump = badabump.cli.app:main',
                     'badabump-ci = badabump.cli.ci_app:main']}

setup_kwargs = {
    'name': 'badabump',
    'version': '21.2.3',
    'description': 'Manage changelog and bump project version number using conventional commits from latest git tag. Support Python & JavaScript projects and CalVer & SemVer schemas. Designed to run at GitHub Actions.',
    'long_description': '# badabump\n\n[![CalVer](https://img.shields.io/badge/calver-YY.MINOR.MICRO-22bfda)](https://calver.org)\n[![CI Workflow](https://github.com/playpauseandstop/badabump/workflows/ci/badge.svg)](https://github.com/playpauseandstop/badabump/actions?query=workflow%3A%22ci%22)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com)\n[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](https://github.com/commitizen-tools/commitizen#integrating-with-pre-commit)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Latest Version](https://img.shields.io/pypi/v/badabump.svg)](https://pypi.org/project/badabump/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/badabump.svg)](https://pypi.org/project/badabump/)\n[![BSD License](https://img.shields.io/pypi/l/badabump.svg)](https://github.com/playpauseandstop/badabump/blob/master/LICENSE)\n[![Coverage](https://coveralls.io/repos/playpauseandstop/badabump/badge.svg?branch=master&service=github)](https://coveralls.io/github/playpauseandstop/badabump)\n\nManage changelog and bump project version number using conventional commits from latest git tag. Support Python & JavaScript projects and CalVer & SemVer schemas. Designed to run at GitHub Actions.\n',
    'author': 'Igor Davydenko',
    'author_email': 'iam@igordavydenko.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://igordavydenko.com/projects/#badabump',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
