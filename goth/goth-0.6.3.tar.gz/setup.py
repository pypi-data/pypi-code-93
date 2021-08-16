# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['goth',
 'goth.api_monitor',
 'goth.assertions',
 'goth.runner',
 'goth.runner.cli',
 'goth.runner.container',
 'goth.runner.download',
 'goth.runner.probe']

package_data = \
{'': ['*'],
 'goth': ['default-assets/*',
          'default-assets/docker/*',
          'default-assets/keys/*',
          'default-assets/provider/*',
          'default-assets/web-root/*',
          'default-assets/web-root/upload/*']}

install_requires = \
['aiohttp==3.7.4',
 'ansicolors>=1.1.0,<2.0.0',
 'docker-compose>=1.29,<2.0',
 'docker>=5.0,<6.0',
 'dpath>=2.0,<3.0',
 'func_timeout==4.3.5',
 'ghapi>=0.1.16,<0.2.0',
 'mitmproxy>=5.3,<6.0',
 'pyyaml>=5.4,<6.0',
 'transitions>=0.8,<0.9',
 'typing_extensions==3.7.4.3',
 'urllib3>=1.26,<2.0',
 'ya-aioclient>=0.6,<0.7']

setup_kwargs = {
    'name': 'goth',
    'version': '0.6.3',
    'description': 'Golem Test Harness - integration testing framework',
    'long_description': '# Golem Test Harness\n\n![codestyle](https://github.com/golemfactory/goth/workflows/codestyle/badge.svg?event=push)\n![test](https://github.com/golemfactory/goth/workflows/test/badge.svg?event=push)\n[![PyPI version](https://badge.fury.io/py/goth.svg)](https://badge.fury.io/py/goth)\n[![GitHub license](https://img.shields.io/github/license/golemfactory/goth)](https://github.com/golemfactory/goth/blob/master/LICENSE)\n\n`goth` is an integration testing framework intended to aid the development process of [`yagna`](https://github.com/golemfactory/yagna) itself, as well as apps built on top of it.\n\n## How it works\n\nKey features:\n- creates a fully local, isolated network of Golem nodes including an Ethereum blockchain (through [`ganache`](https://www.trufflesuite.com/ganache))\n- provides an interface for controlling the local Golem nodes using either `yagna`\'s REST API or CLI\n- includes tools for defining complex integration testing scenarios, e.g. HTTP traffic and log assertions\n- configurable through a YAML file as well as using a number of CLI parameters\n\nWithin a single `goth` invocation (i.e. test session) the framework executes all tests which are defined in its given directory tree.\n\nInternally, `goth` uses `pytest`, therefore each integration test is defined as a function with the `test_` prefix in its name.\n\nEvery test run consists of the following steps:\n1. `docker-compose` is used to start the so-called "static" containers (e.g. local blockchain, HTTP proxy) and create a common Docker network for all containers participating in the given test.\n2. The test runner creates a number of Yagna containers (as defined in `goth-config.yml`) which are then connected to the `docker-compose` network.\n3. For each Yagna container started an interface object called a `Probe` is created and made available inside the test via the `Runner` object.\n4. The integration test scenario is executed as defined in the test function itself.\n5. Once the test is finished, all previously started Docker containers (both "static" and "dynamic") are removed and other cleanup is performed before repeating these steps for the next test.\n\n## Requirements\n- Linux (tested on Ubuntu 18.04 and 20.04)\n- Python 3.8+\n- Docker\n\n#### Python 3.8+\nYou can check your currently installed Python version by running:\n```\npython3 --version\n```\n\nIf you don\'t have Python installed, download the appropriate package and follow instructions from the [releases page](https://www.python.org/downloads/).\n#### Docker\nTo run `goth` you will need to have Docker installed. To install the Docker engine on your system follow these [instructions](https://docs.docker.com/engine/install/).\n\nTo verify your installation you can run the `hello-world` Docker image:\n```\ndocker run hello-world\n```\n\n## Installation\n`goth` is available as a PyPI package:\n```\npip install goth\n```\n\nIt is encouraged to use a Python virtual environment.\n\n## Usage\n\n### Getting a GitHub API token\nWhen starting the local Golem network, `goth` uses the GitHub API to fetch metadata and download artifacts and images. Though all of these assets are public, using this API still requires basic authentication. Therefore, you need to provide `goth` with a personal access token.\n\nTo generate a new token, go to your account\'s [developer settings](https://github.com/settings/tokens).\n\nYou will need to grant your new token the `public_repo` scope, as well as the `read:packages` scope. The packages scope is required in order to pull Docker images from GitHub.\n\nOnce your token is generated you need to do two things:\n1. Log in to GitHub\'s Docker registry by calling: `docker login docker.pkg.github.com -u {username}`, replacing `{username}` with your GitHub username and pasting in your access token as the password. You only need to do this once on your machine.\n2. Export an environment variable named `GITHUB_API_TOKEN` and use the access token as its value. This environment variable will need to be available in the shell from which you run `goth`.\n\n### Starting a local network\n\nFirst, create a copy of the default assets:\n```\npython -m goth create-assets your/output/dir\n```\n\nWhere `your/output/dir` is the path to a directory under which the default assets should be created. The path can be relative and it cannot be pointing to an existing directory.\nThese assets do not need to be re-created between test runs.\n\nWith the default assets created you can run the local test network like so:\n\n```\npython -m goth start your/output/dir/goth-config.yml\n```\n\nIf everything went well you should see the following output:\n```\nLocal goth network ready!\n\nYou can now load the requestor configuration variables to your shell:\n\nsource /tmp/goth_interactive.env\n\nAnd then run your requestor agent from that same shell.\n\nPress Ctrl+C at any moment to stop the local network.\n```\n\nThis is a special case of `goth`\'s usage. Running this command does not execute a test, but rather sets up a local Golem network which can be used for debugging purposes. The parameters required to connect to the requestor `yagna` node running in this network are output to the file `/tmp/goth_interactive.env` and can be `source`d from your shell.\n\n### Creating and running test cases\nTake a look at the `yagna` integration tests [`README`](https://github.com/golemfactory/yagna/blob/master/goth_tests/README.md) to learn more about writing and launching your own test cases.\n\n### Logs from `goth` tests\nAll containers launched during an integration test record their logs in a pre-determined location. By default, this location is: `$TEMP_DIR/goth-tests`, where `$TEMP_DIR` is the path of the directory used for temporary files.\n\nThis path will depend either on the shell environment or the operating system on which the tests are being run (see [`tempfile.gettempdir`](https://docs.python.org/3/library/tempfile.html) for more details).\n\n#### Log directory structure\n```\n.\n└── goth_20210420_093848+0000\n    ├── runner.log                      # debug console logs from the entire test session\n    ├── test_e2e_vm                     # directory with logs from a single test\n    │\xa0\xa0 ├── ethereum.log\n    │\xa0\xa0 ├── provider_1.log              # debug logs from a single yagna node\n    │\xa0\xa0 ├── provider_1_ya-provider.log  # debug logs from an agent running in a yagna node\n    │\xa0\xa0 ├── provider_2.log\n    │\xa0\xa0 ├── provider_2_ya-provider.log\n    │\xa0\xa0 ├── proxy-nginx.log\n    │\xa0\xa0 ├── proxy.log                   # HTTP traffic going into the yagna daemons recorded by a "sniffer" proxy\n    │\xa0\xa0 ├── requestor.log\n    │\xa0\xa0 ├── router.log\n    │\xa0\xa0 ├── test.log                    # debug console logs from this test case only, duplicated in `runner.log`\n    │\xa0\xa0 └── zksync.log\n    └── test_e2e_wasi\n        └── ...\n```\n\n### Test configuration\n\n#### `goth-config.yml`\n`goth` can be configured using a YAML file. The default `goth-config.yml` is located in `goth/default-assets/goth-config.yml` and looks something like this:\n```\ndocker-compose:\n\n  docker-dir: "docker"                          # Where to look for docker-compose.yml and Dockerfiles\n\n  build-environment:                            # Fields related to building the yagna Docker image\n    # binary-path: ...\n    # deb-path: ...\n    # branch: ...\n    # commit-hash: ...\n    # release-tag: ...\n\n  compose-log-patterns:                         # Log message patterns used for container ready checks\n    ethereum: ".*Wallets supplied."\n    ...\n\nkey-dir: "keys"                                 # Where to look for pre-funded Ethereum keys\n\nnode-types:                                     # User-defined node types to be used in `nodes`\n  - name: "Requestor"\n    class: "goth.runner.probe.RequestorProbe"\n\n  - name: "Provider"\n    class: "goth.runner.probe.ProviderProbe"\n    mount: ...\n\nnodes:                                          # List of yagna nodes to be run in the test\n  - name: "requestor"\n    type: "Requestor"\n\n  - name: "provider-1"\n    type: "Provider"\n    use-proxy: True\n```\n\nWhen you generate test assets using the command `python -m goth create-assets your/output/dir`, this default config file will be present in the output location of your choice. You can make changes to that generated file and always fall back to the default one by re-generating the assets.\n\n## Local development setup\n\n### Poetry\n`goth` uses [`poetry`](https://python-poetry.org/) to manage its dependencies and provide a runner for common tasks.\n\nIf you don\'t have `poetry` available on your system then follow its [installation instructions](https://python-poetry.org/docs/#installation) before proceeding.\nVerify your installation by running:\n```\npoetry --version\n```\n\n### Project dependencies\nTo install the project\'s dependencies run:\n```\npoetry install\n```\nBy default, `poetry` looks for the required Python version on your `PATH` and creates a virtual environment for the project if there\'s none active (or already configured by Poetry).\n\nAll of the project\'s dependencies will be installed to that virtual environment.\n',
    'author': 'Golem Factory',
    'author_email': 'contact@golem.network',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/golemfactory/goth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
