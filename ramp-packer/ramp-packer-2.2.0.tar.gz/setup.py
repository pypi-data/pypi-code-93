# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['RAMP', 'RAMP.disposableredis']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==5.3.1',
 'click>=6.7.0,<7.0.0',
 'redis>=3.5.3,<4.0.0',
 'semantic-version>=2.8.5,<3.0.0',
 'typing>=3.0.0,<4.0.0']

entry_points = \
{'console_scripts': ['ramp = RAMP.ramp:ramp']}

setup_kwargs = {
    'name': 'ramp-packer',
    'version': '2.2.0',
    'description': 'Packs for Redis modules into a distributable format',
    'long_description': "[![license](https://img.shields.io/github/license/RedisLabsModules/RAMP.svg)](https://github.com/RedisLabsModules/RAMP)\n[![CircleCI](https://circleci.com/gh/RedisLabsModules/RAMP/tree/master.svg?style=svg)](https://circleci.com/gh/RedisLabsModules/RAMP/tree/master)\n[![GitHub issues](https://img.shields.io/github/release/RedisLabsModules/RAMP.svg)](https://github.com/RedisLabsModules/RAMP/releases/latest)\n[![Codecov](https://codecov.io/gh/RedisLabsModules/RAMP/branch/master/graph/badge.svg)](https://codecov.io/gh/RedisLabsModules/RAMP)\n\n\n# RAMP\n\nRedis Automatic Module Packaging\n\nSimilar to `npm init`, this packer bundles Redis Modules for later distribution.\n\nIt gathers information from modules e.g.\nmodule's name, command list, version and additional metadata.\n\n## Prerequisites\n\nMake sure redis-server is on your PATH\n\n```sh\nexport PATH=$PATH:<PATH_TO_REDIS>\n```\n\n## Install\n\nYou can either use pip install or the setup.py script\n\n```sh\npip install ramp-packer\n```\n\n```sh\npython setup.py install\n```\n\n## Usage\n\n## Manifest mode\n\n```sh\nramp pack <PATH_TO_RedisModule.so> -m <PATH_TO_Manifest.yml>\n```\n\nmanifest.yml should specify your module's attributes, the ones you would specify manualy if you were to use\nthe Command line mode, see Full usage options and manifest.yml for a reference.\n\n## Command line mode\n\n```sh\nramp pack <PATH_TO_RedisModule.so> -a <author> -e <email> -A <architecture> -d <description> -h <homepage> -l <license> -c <cmdargs> -r <redis-min-version>\n```\n\n## Full usage options\n\n```sh\nUsage: ramp [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  pack\n  unpack\n  validate\n  version\n```\n\n## Packing\n\n```sh\nUsage: ramp pack [OPTIONS] MODULE\n\nOptions:\n  -o, --output TEXT               output file name\n  -v, --verbose                   verbose mode: print the resulting metadata\n  -m, --manifest FILENAME         generate package from manifest\n  -d, --display-name TEXT         name for display purposes\n  -a, --author TEXT               module author\n  -e, --email TEXT                authors email\n  -A, --architecture TEXT         module compiled on i386/x86_64 arch\n  -D, --description TEXT          short description\n  -h, --homepage TEXT             module homepage\n  -l, --license TEXT              license\n  -c, --cmdargs TEXT              module command line arguments\n  -r, --redis-min-version TEXT    redis minimum version\n  -R, --redis-pack-min-version TEXT\n                                  redis pack minimum version\n  -cc, --config-command TEXT      command to configure module at run time\n\n  -O, --os TEXT                   build target OS (Darwin/Linux)\n  -C, --capabilities TEXT         comma seperated list of module capabilities\n  --help                          Show this message and exit.\n```\n\n## Module Capabilities\n\nFollowing is a list of capabilities which can be specified for a module\n\ncapability | description |\n---------- | ----------- |\ntypes | module has its own types and not only operate on existing redis types|\nno_multi_key | module has no methods that operate on multiple keys|\nreplica_of | module can work with replicaof capability when it is loaded into a source or a destination database|\nbackup_restore | module can work with import/export capability|\neviction_expiry | module is able to handle eviction and expiry without an issue|\nreshard_rebalance | module is able to operate in a database that is resharded and rebalanced|\nfailover_migrate | module is able to operate in a database that is failing over and migrating|\npersistence_aof | module is able to operate in a database when database chooses AOF persistence option|\npersistence_rdb | module is able to operate in a database when database chooses SNAPSHOT persistence option|\nhash_policy | module is able to operate in a database with a user defined HASH POLICY|\nflash | module is able to operate in a database with Flash memory is enabled or changed over time|\ncrdb | module is able to operate in a database with crdt for the default redis data types|    \nclustering | module is able to operate in a database that is sharded and shards can be migrated|\nintershard_tls | module supports two-way encrypted communication between shards|\n\n## Output\n\nramp pack generates module.zip\n\nWhich contains:\n\n    1. RedisModule.so - original module\n    2. Module.json - module's metadata\n\n## Test\nMake sure redis-server is on your PATH\n\n```sh\nexport PATH=$PATH:<PATH_TO_REDIS>\n```\n\nInstall RAMP\n```sh\npython setup.py install\n```\n\nCompile RedisGraph for your OS v1.0.12 (https://github.com/RedisLabsModules/RedisGraph/tree/v1.0.12)\n\nCopy `redisgraph.so` in `test_module` directory in the root of this project.\n\nRun tests\n```sh\npython test.py\n```\n",
    'author': 'RedisLabs',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
