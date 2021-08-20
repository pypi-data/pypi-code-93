# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncmy', 'asyncmy.constants', 'asyncmy.replication']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'asyncmy',
    'version': '0.1.8',
    'description': 'A fast asyncio MySQL driver',
    'long_description': '# asyncmy - A fast asyncio MySQL driver\n\n[![image](https://img.shields.io/pypi/v/asyncmy.svg?style=flat)](https://pypi.python.org/pypi/asyncmy)\n[![image](https://img.shields.io/github/license/long2ice/asyncmy)](https://github.com/long2ice/asyncmy)\n[![pypi](https://github.com/long2ice/asyncmy/actions/workflows/pypi.yml/badge.svg)](https://github.com/long2ice/asyncmy/actions/workflows/pypi.yml)\n[![ci](https://github.com/long2ice/asyncmy/actions/workflows/ci.yml/badge.svg)](https://github.com/long2ice/asyncmy/actions/workflows/ci.yml)\n\n## Introduction\n\n`asyncmy` is a fast asyncio MySQL driver, which reuse most of [pymysql](https://github.com/PyMySQL/PyMySQL) and rewrite\ncore with [cython](https://cython.org/) to speedup.\n\n## Features\n\n- API compatible with [aiomysql](https://github.com/aio-libs/aiomysql).\n- Fast with [cython](https://cython.org/).\n- MySQL replication protocol support.\n\n## Benchmark\n\nThe result comes from [benchmark](./benchmark), we can know `asyncmy` performs well when compared to other drivers.\n\n> The device is MacBook Pro (13-inch, M1, 2020) 16G and MySQL version is 8.0.23.\n\n![benchmark](./images/benchmark.png)\n\n## Install\n\nJust install from pypi:\n\n```shell\n> pip install asyncmy\n```\n\n## Usage\n\n### Use `connect`\n\n```py\nfrom asyncmy import connect\nfrom asyncmy.cursors import DictCursor\nimport asyncio\n\n\nasync def run():\n    conn = await connect()\n    async with conn.cursor(cursor=DictCursor) as cursor:\n        await cursor.execute("create database if not exists test")\n        await cursor.execute(\n            """CREATE TABLE if not exists test.asyncmy\n    (\n        `id`       int primary key auto_increment,\n        `decimal`  decimal(10, 2),\n        `date`     date,\n        `datetime` datetime,\n        `float`    float,\n        `string`   varchar(200),\n        `tinyint`  tinyint\n    )"""\n        )\n\n\nif __name__ == \'__main__\':\n    asyncio.run(run())\n```\n\n### Use `pool`\n\n```py\nimport asyncmy\nimport asyncio\n\n\nasync def run():\n    pool = await asyncmy.create_pool()\n    async with pool.acquire() as conn:\n        async with conn.cursor() as cursor:\n            await cursor.execute("SELECT 1")\n            ret = await cursor.fetchone()\n            assert ret == (1,)\n\n\nif __name__ == \'__main__\':\n    asyncio.run(run())\n```\n\n## Replication\n\n```py\nfrom asyncmy import connect\nfrom asyncmy.replication import BinLogStream\nimport asyncio\n\n\nasync def run():\n    conn = await connect()\n    ctl_conn = await connect()\n\n    stream = BinLogStream(\n        conn,\n        ctl_conn,\n        1,\n        master_log_file="binlog.000172",\n        master_log_position=2235312,\n        resume_stream=True,\n        blocking=True,\n    )\n    await stream.connect()\n    async for event in stream:\n        print(event)\n\n\nif __name__ == \'__main__\':\n    asyncio.run(run())\n```\n\n## ThanksTo\n\n> asyncmy is build on top of these nice projects.\n\n- [pymysql](https://github/pymysql/PyMySQL), a pure python MySQL client.\n- [aiomysql](https://github.com/aio-libs/aiomysql), a library for accessing a MySQL database from the asyncio.\n- [python-mysql-replication](https://github.com/noplay/python-mysql-replication), pure Python Implementation of MySQL\n  replication protocol build on top of PyMYSQL.\n\n## License\n\nThis project is licensed under the [Apache-2.0](./LICENSE) License.\n',
    'author': 'long2ice',
    'author_email': 'long2ice@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/long2ice/asyncmy',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
