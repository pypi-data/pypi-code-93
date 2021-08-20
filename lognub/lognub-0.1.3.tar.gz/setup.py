# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lognub', 'lognub.captures', 'lognub.handles', 'lognub.patchers']

package_data = \
{'': ['*']}

install_requires = \
['coverage>=5.5,<6.0', 'loguru>=0.5.3,<0.6.0', 'pytest-xdist>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'lognub',
    'version': '0.1.3',
    'description': 'Dumb Log Utlity for personal use',
    'long_description': '# LogNub\n\n[![BuildAndTest](https://github.com/ChethanUK/lognub/actions/workflows/build_test.yml/badge.svg)](https://github.com/ChethanUK/lognub/actions/workflows/build_test.yml) [![PreCommitChecks](https://github.com/ChethanUK/lognub/actions/workflows/code_quality_lint_checkers.yml/badge.svg)](https://github.com/ChethanUK/lognub/actions/workflows/code_quality_lint_checkers.yml) [![CodeQL](https://github.com/ChethanUK/lognub/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/ChethanUK/lognub/actions/workflows/codeql-analysis.yml) [![codecov](https://codecov.io/gh/ChethanUK/lognub/branch/master/graph/badge.svg?token=HRI9hoE5ru)](https://codecov.io/gh/ChethanUK/lognub)\n\nDumb Loguru Wrap Package extracted from different internal package\n\nNOTE: It\'s just curated stuff, Created for personal usage.\n\n## TODO\n\n1. Move logwrap [on top of loguru] extension out as a seperate package.\n1. Add Test containers for [amundsen](https://www.amundsen.io/amundsen/), etc..\n\n## Getting Started\n\n1. Setup [SDKMAN](#setup-sdkman)\n1. Install [Poetry](#poetry)\n1. Install Pre-commit and [follow instruction in here](PreCommit.MD)\n1. Run [tests locally](#running-tests-locally)\n\n### Setup SDKMAN\n\nSDKMAN is a tool for managing parallel Versions of multiple Software Development Kits on any Unix based system. It provides a convenient command line interface for installing, switching, removing and listing Candidates.\nSDKMAN! installs smoothly on Mac OSX, Linux, WSL, Cygwin, etc... Support Bash and ZSH shells.\nSee documentation on the [SDKMAN! website](https://sdkman.io).\n\nOpen your favourite terminal and enter the following:\n\n```bash\n$ curl -s https://get.sdkman.io | bash\nIf the environment needs tweaking for SDKMAN to be installed,\nthe installer will prompt you accordingly and ask you to restart.\n\nNext, open a new terminal or enter:\n\n$ source "$HOME/.sdkman/bin/sdkman-init.sh"\n\nLastly, run the following code snippet to ensure that installation succeeded:\n\n$ sdk version\n```\n\n### Setup Java\n\nInstall Java Now open favourite terminal and enter the following:\n\n```bash\nList the AdoptOpenJDK OpenJDK versions\n$ sdk list java\n\nTo install For Java 11\n$ sdk install java 11.0.10.hs-adpt\n\nTo install For Java 11\n$ sdk install java 8.0.292.hs-adpt\n```\n\n### Poetry\n\nPoetry [Commands](https://python-poetry.org/docs/cli/#search)\n\n```bash\npoetry install\n\npoetry update\n\n# --tree: List the dependencies as a tree.\n# --latest (-l): Show the latest version.\n# --outdated (-o): Show the latest version but only for packages that are outdated.\npoetry show -o\n```\n\n## Running Tests Locally\n\nTake a look at tests in `tests/dataquality` and `tests/jobs`\n\n```bash\n$ poetry run pytest\nRan 95 tests in 96.95s\n```\n',
    'author': 'ChethanUK',
    'author_email': 'chethanuk@outlook.com',
    'maintainer': 'ChethanUK',
    'maintainer_email': 'chethanuk@outlook.com',
    'url': 'https://github.com/ChethanUK/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
