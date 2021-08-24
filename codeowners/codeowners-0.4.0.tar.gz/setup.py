# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['codeowners']

package_data = \
{'': ['*']}

install_requires = \
['typing_extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'codeowners',
    'version': '0.4.0',
    'description': 'Codeowners parser for Python',
    'long_description': '# codeowners [![CircleCI](https://circleci.com/gh/sbdchd/codeowners.svg?style=svg)](https://circleci.com/gh/sbdchd/codeowners) [![pypi](https://img.shields.io/pypi/v/codeowners.svg)](https://pypi.org/project/codeowners/)\n\n> Python codeowners parser based on [softprops\'s Rust\n> library](https://crates.io/crates/codeowners) and [hmarr\'s Go\n> library](https://github.com/hmarr/codeowners/).\n\n## Why?\n\nTo allow Python users to parse [codeowners\nfiles](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/about-code-owners#codeowners-syntax)\nin Python.\n\n## Install\n\n```shell\npip install codeowners\n```\n\n## Usage\n\n```python\nfrom codeowners import CodeOwners\n\nexample_file = """\\\n# owners for js files\n*.js    @ghost\n# python\n*.py user@example.com\n# misc\n/build/logs/ @dmin\ndocs/*  docs@example.com\n"""\n\nowners = CodeOwners(example_file)\nassert owners.of("test.js") ==  [(\'USERNAME\', \'@ghost\')]\n```\n\n## Dev\n\n```shell\npoetry install\n\ns/test\n\ns/lint\n```\n\n## Releasing a New Version\n\n```shell\n# bump version in pyproject.toml\n\n# update CHANGELOG.md\n\n# commit release commit to GitHub\n\n# build and publish\npoetry publish --build\n\n# create a release in the GitHub UI\n```\n',
    'author': 'Steve Dignam',
    'author_email': 'steve@dignam.xyz',
    'url': 'https://github.com/sbdchd/codeowners',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
