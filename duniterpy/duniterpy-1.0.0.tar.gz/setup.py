# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['duniterpy',
 'duniterpy.api',
 'duniterpy.api.bma',
 'duniterpy.api.elasticsearch',
 'duniterpy.api.ws2p',
 'duniterpy.documents',
 'duniterpy.documents.ws2p',
 'duniterpy.grammars',
 'duniterpy.helpers',
 'duniterpy.key']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'base58>=2.1.0,<3.0.0',
 'graphql-core>=3.1.2,<4.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'libnacl>=1.7.2,<2.0.0',
 'mnemonic>=0.19,<0.20',
 'pyaes>=1.6.1,<2.0.0',
 'pypeg2>=2.15.2,<3.0.0',
 'websocket-client>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'duniterpy',
    'version': '1.0.0',
    'description': 'Python library for developers of Duniter clients',
    'long_description': '# DuniterPy\nMost complete client oriented Python library for [Duniter](https://git.duniter.org/nodes/typescript/duniter)/Ğ1 ecosystem.\n\nThis library was originally developed for [Sakia](http://sakia-wallet.org/) desktop client which is now discontinued.\nIt is currently used by following programs:\n- [Tikka](https://git.duniter.org/clients/python), the desktop client (Work In Progress, not yet available).\n- [Silkaj](https://silkaj.duniter.org/), command line client.\n- [Jaklis](https://git.p2p.legal/axiom-team/jaklis), command line client for Cs+/Gchange pods.\n- [Ğ1Dons](https://git.duniter.org/matograine/g1pourboire), Ğ1Dons, paper-wallet generator aimed at giving tips in Ğ1.\n\n## Features\n### Network\n- APIs support: BMA, GVA, WS2P, and CS+:\n  - [Basic Merkle API](https://git.duniter.org/nodes/typescript/duniter/-/blob/dev/doc/HTTP_API.md), first Duniter API to be deprecated\n  - GraphQL Verification API, Duniter API in developement meant to replace BMA. Based on GraphQL.\n  - Websocket to Peer, Duniter inter-nodes (servers) API\n  - Cesium+, non-Duniter API, used to store profile data related to the blockchain as well as ads for Cesium and Ğchange.\n- Non-threaded asynchronous/synchronous connections\n- Support HTTP, HTTPS, and WebSocket transport for the APIs\n- Endpoints management\n\n### Blockchain\n- Support [Duniter blockchain protocol](https://git.duniter.org/documents/rfcs#duniter-blockchain-protocol-dubp)\n- Duniter documents management: transaction, block and WoT documents\n- Multiple authentication methods\n- Duniter signing key\n- Sign/verify and encrypt/decrypt messages with Duniter credentials\n\n## Requirements\n- Python >= 3.6.8\n- [websocket-client](https://pypi.org/project/websocket-client)\n- [jsonschema](https://pypi.org/project/jsonschema)\n- [pyPEG2](https://pypi.org/project/pyPEG2)\n- [attrs](https://pypi.org/project/attrs)\n- [base58](https://pypi.org/project/base58)\n- [libnacl](https://pypi.org/project/libnacl)\n- [pyaes](https://pypi.org/project/pyaes)\n\n## Installation\nYou will require following dependencies:\n```bash\nsudo apt install python3-pip python3-dev python3-wheel libsodium23\n```\n\nYou can install DuniterPy and its dependencies with following command:\n```bash\npip3 install duniterpy --user\n```\n\n## Install the development environment\n- [Install Poetry](https://python-poetry.org/docs/#installation)\n\n## Documentation\n[Online official automaticaly generated documentation](https://clients.duniter.io/python/duniterpy/index.html)\n\n## Examples\nThe [examples folder](https://git.duniter.org/clients/python/duniterpy/tree/master/examples) contains scripts to help you!\n\n- Have a look at the `examples` folder\n- Run examples from parent folder directly\n```bash\npoetry run python examples/request_data.py\n```\n\nOr from Python interpreter:\n```bash\npoetry run python\n>>> import examples\n>>> help(examples)\n>>> examples.create_public_key()\n```\n\n`request_data_async` example requires to be run with `asyncio`:\n```bash\n>>> import examples, asyncio\n>>> asyncio.get_event_loop().run_until_complete(examples.request_data_async())\n```\n\n### How to generate and read locally the autodoc\n\n- Install Sphinx, included into the development dependencies:\n```bash\npoetry install\n```\n\n- Generate documentation\n```bash\npoetry run make docs\n```\n\n- The HTML documentation is generated in `docs/_build/html` folder.\n\n## Development\n* When writing docstrings, use the reStructuredText format recommended by https://www.python.org/dev/peps/pep-0287/#docstring-significant-features\n* Use `make` commands to check the code and the format.\n\n* Install runtime dependencies\n```bash\npoetry install --no-dev\n```\n\n* Before submitting a merge requests, please check the static typing and tests.\n\n* Install dev dependencies\n```bash\npoetry install\n```\n\n* Check static typing with [mypy](http://mypy-lang.org/)\n```bash\nmake check\n```\n\n* Run all unit tests (builtin `unittest` module) with:\n```bash\nmake tests\n```\n\n* Run only some unit tests by passing a special ENV variable:\n```bash\nmake tests TESTS_FILTER=tests.documents.test_block.TestBlock.test_fromraw\n```\n\n## Packaging and deploy\n### PyPI\nChange and commit and tag the new version number (semantic version number)\n```bash\n./release.sh 0.42.3\n```\n\nBuild the PyPI package in the `dist` folder\n```bash\nmake build\n```\n\nDeploy the package to PyPI test repository (prefix the command with a space for the shell to not save it in its history system, since the command contains credentials)\n```bash\n[SPACE]make deploy_test PYPI_TEST_LOGIN=xxxx PYPI_TEST_PASSWORD=xxxx\n```\n\nInstall the package from PyPI test repository\n```bash\npip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.python.org/simple/ duniterpy\n```\n\nDeploy the package on the PyPI repository (prefix the command with a space for the shell to not save it in its history system, since the command contains credentials)\n```bash\n[SPACE]make deploy PYPI_LOGIN=xxxx PYPI_PASSWORD=xxxx\n```\n\n## Packaging status\n[![Packaging status](https://repology.org/badge/vertical-allrepos/python:duniterpy.svg)](https://repology.org/project/python:duniterpy/versions)\n',
    'author': 'inso',
    'author_email': 'insomniak.fr@gmail.com',
    'maintainer': 'vit',
    'maintainer_email': 'vit@free.fr',
    'url': 'https://git.duniter.org/clients/python/duniterpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.8,<4.0.0',
}


setup(**setup_kwargs)
