# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_too_many', 'flake8_too_many.utils']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3.9.2,<4.0.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.8,<0.9']}

entry_points = \
{'flake8.extension': ['TMN = flake8_too_many:Checker']}

setup_kwargs = {
    'name': 'flake8-too-many',
    'version': '0.1.1',
    'description': 'A flake8 plugin that prevents you from writing "too many" bad codes.',
    'long_description': '# flake8-too-many\n\n[![python: 3.6.1+](https://img.shields.io/badge/python->=3.6.1-blue.svg)](https://www.python.org/downloads/)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/queensferryme/flake8-too-many/master.svg)](https://results.pre-commit.ci/latest/github/queensferryme/flake8-too-many/master)\n[![github ci status](https://img.shields.io/github/workflow/status/queensferryme/flake8-too-many/Test?label=test&logo=github&message=passed)](https://github.com/RSSerpent/RSSerpent/actions/workflows/test.yaml)\n[![codecov](https://codecov.io/gh/queensferryme/flake8-too-many/branch/master/graph/badge.svg?token=56VCCB1JUB)](https://codecov.io/gh/queensferryme/flake8-too-many)\n\nA flake8 plugin that prevents you from writing "too many" bad codes.\n\n## Installation\n\nwith `pip`\n\n```shell\npip install flake8-too-many\n```\n\nwith [`poetry`](https://python-poetry.org/)\n\n```shell\npoetry add -D flake8-too-many\n```\n\nwith [`pre-commit`](https://pre-commit.com/) ([doc](https://flake8.pycqa.org/en/latest/user/using-hooks.html))\n\n```yaml\nrepos:\n  - repo: https://github.com/PyCQA/flake8\n    rev: \'\' # pick a git hash/tag\n    hooks:\n      - id: flake8\n        additional_dependencies:\n          # ...\n          - flake8-too-many\n```\n\n## Error Codes\n\n| code   | description                              | example                                                      |\n| ------ | ---------------------------------------- | ------------------------------------------------------------ |\n| TMN001 | function has too many arguments.         | [link](https://github.com/queensferryme/flake8-too-many/blob/master/tests/files/function_arguments.py) |\n| TMN002 | function returns too many values.        | [link](https://github.com/queensferryme/flake8-too-many/blob/master/tests/files/function_return_values.py) |\n| TMN003 | function has too many return statements. | [link](https://github.com/queensferryme/flake8-too-many/blob/master/tests/files/function_return_stmts.py) |\n| TMN004 | unpacking has too many targets.          | [link](https://github.com/queensferryme/flake8-too-many/blob/master/tests/files/unpacking_targets.py) |\n\n\n## Options\n\nThese options could be either passed in as command line flags, or specified in a `.flake8` configuration file.\n\n* `--max-function-arguments`, int, default to 5;\n  * `--ignore-defaulted-arguments`, bool, default to false;\n* `--max-function-return-values`, int, default to 3;\n* `--max-function-return-stmts`, int, default to 3;\n* `--max-unpacking-targets`, int, default to 5.\n\nRun `flake8 -h` for detailed description of each option.\n',
    'author': 'Queensferry',
    'author_email': 'queensferry.me@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/queensferryme/flake8-too-many',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
