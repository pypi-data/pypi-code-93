# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['michelson_kernel',
 'pytezos',
 'pytezos.block',
 'pytezos.cli',
 'pytezos.context',
 'pytezos.contract',
 'pytezos.crypto',
 'pytezos.michelson',
 'pytezos.michelson.instructions',
 'pytezos.michelson.sections',
 'pytezos.michelson.types',
 'pytezos.operation',
 'pytezos.protocol',
 'pytezos.rpc',
 'pytezos.sandbox']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.3.0,<21.0.0',
 'base58>=1.0.3,<2.0.0',
 'bravado>=11.0.3,<12.0.0',
 'bson>=0.5.10,<0.6.0',
 'cached-property>=1.5.2,<2.0.0',
 'cattrs-extras>=0.1.1,<0.2.0',
 'cattrs>=1.3.0,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'deprecation',
 'docker>=4.4.4,<5.0.0',
 'fastecdsa==1.7.5',
 'ipykernel>=5.5.0,<6.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'jupyter-client>=6.1.12,<7.0.0',
 'loguru',
 'mnemonic',
 'netstruct',
 'notebook>=6.3.0,<7.0.0',
 'pendulum',
 'ply',
 'py_ecc',
 'pyblake2>=1.1.2,<2.0.0',
 'pysha3==1.0.2',
 'pysodium==0.7.7',
 'pyyaml',
 'requests>=2.21.0,<3.0.0',
 'secp256k1==0.13.2',
 'simplejson',
 'strict_rfc3339==0.7',
 'tabulate>=0.8.9,<0.9.0',
 'testcontainers>=3.2.0,<4.0.0',
 'tqdm',
 'typing-extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['michelson-kernel = michelson_kernel.cli:cli',
                     'pytezos = pytezos.cli.cli:cli']}

setup_kwargs = {
    'name': 'pytezos',
    'version': '3.2.10',
    'description': 'Python toolkit for Tezos',
    'long_description': "# PyTezos\n\n[![PyPI version](https://badge.fury.io/py/pytezos.svg?)](https://badge.fury.io/py/pytezos)\n[![Tests](https://github.com/baking-bad/pytezos/workflows/Tests/badge.svg?)](https://github.com/baking-bad/pytezos/actions?query=workflow%3ATests)\n[![Docker images](https://github.com/baking-bad/pytezos/workflows/Dockerhub/badge.svg?)](https://hub.docker.com/r/bakingbad/pytezos)\n[![Made With](https://img.shields.io/badge/made%20with-python-blue.svg?)](ttps://www.python.org)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/baking-bad/pytezos/master?filepath=michelson_quickstart.ipynb)\n\n\n* RPC query engine\n* Cryptography\n* Building and parsing operations\n* Smart contract interaction\n* Local forging/packing & vice versa\n* Working with Michelson AST\n\n#### PyTezos CLI\n* Generating contract parameter/storage schema\n* Activating and revealing accounts\n* Deploying contracts (+ GitHub integration)\n\n#### Michelson REPL\n* Builtin interpreter (reimplemented)\n* Set of extra helpers (stack visualization, blockchain context mocking)\n\n#### Michelson Jupyter kernel\n* Custom interpreter with runtime type checker\n* Syntax highlighting, autocomplete with `Tab`\n* In-place docstrings with `Shift+Tab`\n* Macros support\n* Verbose execution logging\n* Debug helpers\n\n#### Michelson integration testing framework\n* Writing integration tests using `unittest` package\n* Simulating contract execution using remote intepreter (via RPC) or builtin one\n\n\n## Installation\n\nYou need to install cryptographic packages before installing the library/building the project:\n\n#### Linux\n\n##### Ubuntu, Debian and other apt-based distributions\n```shell\n$ sudo apt install libsodium-dev libsecp256k1-dev libgmp-dev\n```\n\n##### Arch Linux\n```shell\n$ sudo pacman -Syu --needed libsodium libsecp256k1 gmp\n```\n#### MacOS\n\n[Homebrew](https://brew.sh/) needs to be installed.\n```shell\n$ brew tap cuber/homebrew-libsecp256k1\n$ brew install libsodium libsecp256k1 gmp\n```\n\n#### Windows\n\nThe recommended way is to use WSL and then follow the instructions for Linux,\nbut if you feel lucky you can try to install natively:\n\n1. Install MinGW from [https://osdn.net/projects/mingw/](https://osdn.net/projects/mingw/)\n2. Make sure `C:\\MinGW\\bin` is added to your `PATH`\n3. Download the latest libsodium-X.Y.Z-msvc.zip from [https://download.libsodium.org/libsodium/releases/](https://download.libsodium.org/libsodium/releases/).\n4. Extract the Win64/Release/v143/dynamic/libsodium.dll from the zip file\n5. Copy libsodium.dll to C:\\Windows\\System32\\libsodium.dll\n\n### From PyPi\n\n```shell\n$ pip install wheel setuptools\n$ pip install pytezos\n```\n\n\n### [Google Colab](https://colab.research.google.com)\n\n`````python\n>>> !apt install libsodium-dev libsecp256k1-dev libgmp-dev\n>>> !pip install pytezos\n`````\n\n### Docker container\nVerified & minified images for CI/CD https://hub.docker.com/r/bakingbad/pytezos/tags\n```shell\n$ # 1. Use image from registry\n$ docker pull bakingbad/pytezos\n$ # or build it yourself\n$ docker build . -t pytezos\n$ # 2. Use included docker-compose.yml\n$ docker-compose up -d notebook\n```\n\n### Building from sources\n\nRequirements:\n* Python 3.7+\n* [Poetry](https://python-poetry.org/docs/#installation)\n* libsodium, libsecp256k1, gmp\n* make\n\n```shell\n$ # prepare environment\n$ make install\n# # run full CI with tests\n$ make\n```\n\n## Quick start\nRead [quick start guide](https://pytezos.org/quick_start.html)  \nLearn how to [enable Jupyter with Michelson](./src/michelson_kernel/README.md)\n\n## API reference\nCheck out a complete [API reference](https://pytezos.org/contents.html)\n\n### Inline documentation\nIf you are working in Jupyter/Google Colab or any other interactive console, \nyou can display documentation for a particular class/method:\n\n```python\n>>> from pytezos import pytezos\n>>> pytezos\n```\n\n### Publications\n\n* Pytezos 2.0 release with embedded docs and smart contract interaction engine  \nhttps://medium.com/coinmonks/high-level-interface-for-michelson-contracts-and-not-only-7264db76d7ae\n\n* Materials from TQuorum:Berlin workshop - building an app on top of PyTezos and ConseilPy  \nhttps://medium.com/coinmonks/atomic-tips-berlin-workshop-materials-c5c8ee3f46aa\n\n* Materials from the EETH hackathon - setting up a local development infrastructure, deploying and interacting with a contract  \nhttps://medium.com/tezoscommons/preparing-for-the-tezos-hackathon-with-baking-bad-45f2d5fca519\n\n* Introducing integration testing engine  \nhttps://medium.com/tezoscommons/testing-michelson-contracts-with-pytezos-513718499e93\n\n### Contact\n* Telegram chat: [@baking_bad_chat](https://t.me/baking_bad_chat)\n* Slack channel: [#baking-bad](https://tezos-dev.slack.com/archives/CV5NX7F2L)\n\n## Credits\n* The project was initially started by Arthur Breitman, now it's maintained by Baking Bad team.\n* Baking Bad is supported by Tezos Foundation\n* Michelson test set from the Tezos repo is used to ensure the interpreter workability\n* Michelson structured documentation by Nomadic Labs is used for inline help\n",
    'author': 'Michael Zaikin',
    'author_email': 'mz@baking-bad.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pytezos.org',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
