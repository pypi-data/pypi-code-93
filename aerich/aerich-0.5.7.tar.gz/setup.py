# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aerich',
 'aerich.ddl',
 'aerich.ddl.mysql',
 'aerich.ddl.postgres',
 'aerich.ddl.sqlite']

package_data = \
{'': ['*']}

install_requires = \
['click', 'ddlparse', 'dictdiffer', 'pydantic', 'tortoise-orm']

extras_require = \
{'aiomysql': ['aiomysql'], 'asyncpg': ['asyncpg']}

entry_points = \
{'console_scripts': ['aerich = aerich.cli:main']}

setup_kwargs = {
    'name': 'aerich',
    'version': '0.5.7',
    'description': 'A database migrations tool for Tortoise ORM.',
    'long_description': '# Aerich\n\n[![image](https://img.shields.io/pypi/v/aerich.svg?style=flat)](https://pypi.python.org/pypi/aerich)\n[![image](https://img.shields.io/github/license/tortoise/aerich)](https://github.com/tortoise/aerich)\n[![image](https://github.com/tortoise/aerich/workflows/pypi/badge.svg)](https://github.com/tortoise/aerich/actions?query=workflow:pypi)\n[![image](https://github.com/tortoise/aerich/workflows/ci/badge.svg)](https://github.com/tortoise/aerich/actions?query=workflow:ci)\n\n## Introduction\n\nAerich is a database migrations tool for Tortoise-ORM, which is like alembic for SQLAlchemy, or like Django ORM with\nit\\\'s own migration solution.\n\n## Install\n\nJust install from pypi:\n\n```shell\n> pip install aerich\n```\n\n## Quick Start\n\n```shell\n> aerich -h\n\nUsage: aerich [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  -V, --version      Show the version and exit.\n  -c, --config TEXT  Config file.  [default: aerich.ini]\n  --app TEXT         Tortoise-ORM app name.\n  -n, --name TEXT    Name of section in .ini file to use for aerich config.\n                     [default: aerich]\n\n  -h, --help         Show this message and exit.\n\nCommands:\n  downgrade  Downgrade to specified version.\n  heads      Show current available heads in migrate location.\n  history    List all migrate items.\n  init       Init config file and generate root migrate location.\n  init-db    Generate schema and generate app migrate location.\n  inspectdb  Introspects the database tables to standard output as...\n  migrate    Generate migrate changes file.\n  upgrade    Upgrade to specified version.\n```\n\n## Usage\n\nYou need add `aerich.models` to your `Tortoise-ORM` config first. Example:\n\n```python\nTORTOISE_ORM = {\n    "connections": {"default": "mysql://root:123456@127.0.0.1:3306/test"},\n    "apps": {\n        "models": {\n            "models": ["tests.models", "aerich.models"],\n            "default_connection": "default",\n        },\n    },\n}\n```\n\n### Initialization\n\n```shell\n> aerich init -h\n\nUsage: aerich init [OPTIONS]\n\n  Init config file and generate root migrate location.\n\nOOptions:\n  -t, --tortoise-orm TEXT  Tortoise-ORM config module dict variable, like\n                           settings.TORTOISE_ORM.  [required]\n\n  --location TEXT          Migrate store location.  [default: ./migrations]\n  -s, --src_folder TEXT    Folder of the source, relative to the project root.\n  -h, --help               Show this message and exit.\n```\n\nInitialize the config file and migrations location:\n\n```shell\n> aerich init -t tests.backends.mysql.TORTOISE_ORM\n\nSuccess create migrate location ./migrations\nSuccess generate config file aerich.ini\n```\n\n### Init db\n\n```shell\n> aerich init-db\n\nSuccess create app migrate location ./migrations/models\nSuccess generate schema for app "models"\n```\n\nIf your Tortoise-ORM app is not the default `models`, you must specify the correct app via `--app`,\ne.g. `aerich --app other_models init-db`.\n\n### Update models and make migrate\n\n```shell\n> aerich migrate --name drop_column\n\nSuccess migrate 1_202029051520102929_drop_column.sql\n```\n\nFormat of migrate filename is\n`{version_num}_{datetime}_{name|update}.sql`.\n\nIf `aerich` guesses you are renaming a column, it will ask `Rename {old_column} to {new_column} [True]`. You can choose\n`True` to rename column without column drop, or choose `False` to drop the column then create. Note that the latter may\nlose data.\n\n### Upgrade to latest version\n\n```shell\n> aerich upgrade\n\nSuccess upgrade 1_202029051520102929_drop_column.sql\n```\n\nNow your db is migrated to latest.\n\n### Downgrade to specified version\n\n```shell\n> aerich downgrade -h\n\nUsage: aerich downgrade [OPTIONS]\n\n  Downgrade to specified version.\n\nOptions:\n  -v, --version INTEGER  Specified version, default to last.  [default: -1]\n  -d, --delete           Delete version files at the same time.  [default:\n                         False]\n\n  --yes                  Confirm the action without prompting.\n  -h, --help             Show this message and exit.\n```\n\n```shell\n> aerich downgrade\n\nSuccess downgrade 1_202029051520102929_drop_column.sql\n```\n\nNow your db is rolled back to the specified version.\n\n### Show history\n\n```shell\n> aerich history\n\n1_202029051520102929_drop_column.sql\n```\n\n### Show heads to be migrated\n\n```shell\n> aerich heads\n\n1_202029051520102929_drop_column.sql\n```\n\n### Inspect db tables to TortoiseORM model\n\nCurrently `inspectdb` only supports MySQL.\n\n```shell\nUsage: aerich inspectdb [OPTIONS]\n\n  Introspects the database tables to standard output as TortoiseORM model.\n\nOptions:\n  -t, --table TEXT  Which tables to inspect.\n  -h, --help        Show this message and exit.\n```\n\nInspect all tables and print to console:\n\n```shell\naerich --app models inspectdb\n```\n\nInspect a specified table in the default app and redirect to `models.py`:\n\n```shell\naerich inspectdb -t user > models.py\n```\n\nNote that this command is limited and cannot infer some fields, such as `IntEnumField`, `ForeignKeyField`, and others.\n\n### Multiple databases\n\n```python\ntortoise_orm = {\n    "connections": {\n        "default": expand_db_url(db_url, True),\n        "second": expand_db_url(db_url_second, True),\n    },\n    "apps": {\n        "models": {"models": ["tests.models", "aerich.models"], "default_connection": "default"},\n        "models_second": {"models": ["tests.models_second"], "default_connection": "second", },\n    },\n}\n```\n\nYou only need to specify `aerich.models` in one app, and must specify `--app` when running `aerich migrate` and so on.\n\n## Restore `aerich` workflow\n\nIn some cases, such as broken changes from upgrade of `aerich`, you can\'t run `aerich migrate` or `aerich upgrade`, you\ncan make the following steps:\n\n1. drop `aerich` table.\n2. delete `migrations/{app}` directory.\n3. rerun `aerich init-db`.\n\nNote that these actions is safe, also you can do that to reset your migrations if your migration files is too many.\n\n## Use `aerich` in application\n\nYou can use `aerich` out of cli by use `Command` class.\n\n```python\nfrom aerich import Command\n\ncommand = Command(tortoise_config=config, app=\'models\')\nawait command.init()\nawait command.migrate(\'test\')\n```\n\n## License\n\nThis project is licensed under the\n[Apache-2.0](https://github.com/long2ice/aerich/blob/master/LICENSE) License.\n',
    'author': 'long2ice',
    'author_email': 'long2ice@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tortoise/aerich',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
